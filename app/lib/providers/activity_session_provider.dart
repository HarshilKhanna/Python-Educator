import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/activity.dart';
import '../services/api_client.dart';
import '../services/auth_service.dart';
import '../services/offline_queue.dart';

// ── State ────────────────────────────────────────────────────────────────────

/// Immutable snapshot of the active practice session.
class ActivitySessionState {
  final List<Activity> activities;
  final int currentIndex;
  final String? selectedAnswer; // null ⟹ not yet answered
  final bool isLoading;
  final String? error;
  final bool isComplete;

  // ── Streak / mastery ──────────────────────────────────────────────────────

  /// Consecutive correct answers in this session.
  final int streak;
  /// Best streak achieved this session.
  final int bestStreak;
  /// Mastery value returned from the backend (0.0–1.0).
  final double mastery;
  /// Mastery value at the very start of the session (for delta calculation).
  final double initialMastery;
  /// Correct answers this session.
  final int correctCount;
  /// Incorrect answers this session.
  final int incorrectCount;

  // ── Adaptive mode ─────────────────────────────────────────────────────────

  /// When true, the session was seeded by the Pedagogical Agent.
  final bool isAdaptive;
  /// Reason string from the Pedagogical Agent (shown below topic label).
  final String? agentReason;
  /// Recommendation returned by the Pedagogical Agent at session start.
  /// Used to populate the end-of-session "What's next?" section.
  final NextActivityRecommendation? nextRecommendation;

  // ── Connectivity / auth ───────────────────────────────────────────────────

  /// True if the last submission is queued offline.
  final bool isOffline;
  /// True if the offline queue attempted to sync but the token is expired.
  final bool needsRelogin;

  // ── Metacognitive confidence ──────────────────────────────────────────────

  /// Student's self-reported confidence for the current activity (0–1), set
  /// before they select their answer. Sent alongside the submission.
  final double? pendingConfidence;

  // ── Struggle detection ────────────────────────────────────────────────────

  /// Number of wrong attempts on the current activity.
  final int wrongAttemptsOnCurrent;
  /// Whether the struggle intervention has already been shown for this activity.
  final bool struggleShown;

  const ActivitySessionState({
    this.activities = const [],
    this.currentIndex = 0,
    this.selectedAnswer,
    this.isLoading = true,
    this.error,
    this.isComplete = false,
    this.streak = 0,
    this.bestStreak = 0,
    this.mastery = 0.0,
    this.initialMastery = 0.0,
    this.correctCount = 0,
    this.incorrectCount = 0,
    this.isAdaptive = false,
    this.agentReason,
    this.nextRecommendation,
    this.isOffline = false,
    this.needsRelogin = false,
    this.pendingConfidence,
    this.wrongAttemptsOnCurrent = 0,
    this.struggleShown = false,
  });

  // ── Derived state ──────────────────────────────────────────────────────────

  bool get isAnswered => selectedAnswer != null;

  bool get isCorrect {
    final act = currentActivity;
    if (act == null || selectedAnswer == null) return false;
    return selectedAnswer == act.correctAnswer;
  }

  bool get isLastActivity =>
      activities.isEmpty || currentIndex >= activities.length - 1;

  Activity? get currentActivity =>
      activities.isEmpty ? null : activities[currentIndex];

  /// Progress as mastery DELTA from session start (not completion ratio).
  /// Clamped to [0, 1] so it never goes negative in the bar.
  double get progress => (mastery - initialMastery).clamp(0.0, 1.0);

  /// Raw completion ratio for the secondary "questions done" indicator.
  double get completionProgress =>
      activities.isEmpty ? 0 : (currentIndex + 1) / activities.length;

  /// Whether struggle detection should fire:
  /// ≥2 wrong attempts on the current activity and intervention not yet shown.
  bool get shouldShowStruggle =>
      wrongAttemptsOnCurrent >= 2 && !struggleShown;

  // ── Copy helper ────────────────────────────────────────────────────────────

  ActivitySessionState copyWith({
    List<Activity>? activities,
    int? currentIndex,
    Object? selectedAnswer = _sentinel,
    bool? isLoading,
    String? error,
    bool? isComplete,
    int? streak,
    int? bestStreak,
    double? mastery,
    double? initialMastery,
    int? correctCount,
    int? incorrectCount,
    bool? isAdaptive,
    Object? agentReason = _sentinel,
    Object? nextRecommendation = _sentinel,
    bool? isOffline,
    bool? needsRelogin,
    Object? pendingConfidence = _sentinel,
    int? wrongAttemptsOnCurrent,
    bool? struggleShown,
  }) {
    return ActivitySessionState(
      activities:              activities              ?? this.activities,
      currentIndex:            currentIndex            ?? this.currentIndex,
      selectedAnswer:          selectedAnswer == _sentinel ? this.selectedAnswer : selectedAnswer as String?,
      isLoading:               isLoading               ?? this.isLoading,
      error:                   error                   ?? this.error,
      isComplete:              isComplete              ?? this.isComplete,
      streak:                  streak                  ?? this.streak,
      bestStreak:              bestStreak              ?? this.bestStreak,
      mastery:                 mastery                 ?? this.mastery,
      initialMastery:          initialMastery          ?? this.initialMastery,
      correctCount:            correctCount            ?? this.correctCount,
      incorrectCount:          incorrectCount          ?? this.incorrectCount,
      isAdaptive:              isAdaptive              ?? this.isAdaptive,
      agentReason:             agentReason == _sentinel ? this.agentReason : agentReason as String?,
      nextRecommendation:      nextRecommendation == _sentinel ? this.nextRecommendation : nextRecommendation as NextActivityRecommendation?,
      isOffline:               isOffline               ?? this.isOffline,
      needsRelogin:            needsRelogin            ?? this.needsRelogin,
      pendingConfidence:       pendingConfidence == _sentinel ? this.pendingConfidence : pendingConfidence as double?,
      wrongAttemptsOnCurrent:  wrongAttemptsOnCurrent  ?? this.wrongAttemptsOnCurrent,
      struggleShown:           struggleShown           ?? this.struggleShown,
    );
  }
}

const _sentinel = Object();

// ── Notifier ─────────────────────────────────────────────────────────────────

class ActivitySessionNotifier extends Notifier<ActivitySessionState> {
  @override
  ActivitySessionState build() => const ActivitySessionState();

  @visibleForTesting
  void loadActivities(List<Activity> activities) {
    state = ActivitySessionState(
      activities: activities,
      currentIndex: 0,
      isLoading: false,
    );
  }

  // ── Fetch helpers ─────────────────────────────────────────────────────────

  /// Fetch activities via the Pedagogical Agent (adaptive mode).
  ///
  /// 1. Calls GET /activities/next to get the agent's recommendation.
  /// 2. Calls GET /activities?topic_id=<recommended> to get the full list.
  /// 3. Sorts the list so the recommended activity_type comes first.
  Future<void> fetchAdaptiveActivities() async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      // 1. Ask the Pedagogical Agent
      final rec = await apiClient.fetchNextActivity();

      // 2. Fetch activities for the recommended topic
      final all = await apiClient.fetchActivities(rec.topicId);

      // 3. Stable-sort: recommended type first, then by original order
      final sorted = [...all]..sort((a, b) {
          final aMatch = a.activityType == rec.activityType ? 0 : 1;
          final bMatch = b.activityType == rec.activityType ? 0 : 1;
          return aMatch.compareTo(bMatch);
        });

      // Sync offline queue on reconnect
      await offlineQueue.syncQueue(onTokenExpired: _handleTokenExpired);

      state = ActivitySessionState(
        activities: sorted,
        currentIndex: 0,
        isLoading: false,
        isAdaptive: true,
        agentReason: rec.reason,
        nextRecommendation: rec,
        mastery: state.mastery,
        initialMastery: state.mastery,
      );
    } on AuthException {
      state = state.copyWith(isLoading: false, needsRelogin: true);
    } catch (e) {
      state = ActivitySessionState(
        isLoading: false,
        error: 'Failed to load adaptive session: $e',
      );
    }
  }

  /// Fetch a flat list of activities for [topicId] (manual / topic-select mode).
  Future<void> fetchActivities(String topicId) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final activities = await apiClient.fetchActivities(topicId);
      await offlineQueue.syncQueue(onTokenExpired: _handleTokenExpired);
      state = ActivitySessionState(
        activities: activities,
        currentIndex: 0,
        isLoading: false,
        isAdaptive: false,
        mastery: state.mastery,
        initialMastery: state.mastery,
      );
    } on AuthException {
      state = state.copyWith(isLoading: false, needsRelogin: true);
    } catch (e) {
      state = ActivitySessionState(
        isLoading: false,
        error: 'Failed to load activities: $e',
      );
    }
  }

  /// Surfaced to the UI on asset-loading failure.
  void setError(String message) {
    state = ActivitySessionState(isLoading: false, error: message);
  }

  /// Clear the re-login flag (called after the user has logged back in).
  void clearReloginFlag() {
    state = state.copyWith(needsRelogin: false);
  }

  // ── Metacognitive confidence ──────────────────────────────────────────────

  /// Set the student's self-reported confidence before they answer.
  void setPendingConfidence(double value) {
    state = state.copyWith(pendingConfidence: value);
  }

  void clearPendingConfidence() {
    state = state.copyWith(pendingConfidence: null);
  }

  // ── Struggle detection ────────────────────────────────────────────────────

  /// Called by the UI after it has shown the struggle intervention card.
  void markStruggleShown() {
    state = state.copyWith(struggleShown: true);
  }

  // ── Answer selection ──────────────────────────────────────────────────────

  /// Lock-once: only the first tap registers.
  /// Submits the answer optimistically and updates mastery from backend async.
  void selectAnswer(String answer) {
    if (state.isAnswered) return;

    final activity = state.currentActivity;
    if (activity == null) return;

    final correct = answer == activity.correctAnswer;
    final newStreak = correct ? state.streak + 1 : 0;
    final newBest   = newStreak > state.bestStreak ? newStreak : state.bestStreak;
    final newCorrect   = state.correctCount + (correct ? 1 : 0);
    final newIncorrect = state.incorrectCount + (correct ? 0 : 1);
    final newWrong  = correct ? 0 : state.wrongAttemptsOnCurrent + 1;

    // Optimistic UI update
    state = state.copyWith(
      selectedAnswer: answer,
      streak:         newStreak,
      bestStreak:     newBest,
      correctCount:   newCorrect,
      incorrectCount: newIncorrect,
      wrongAttemptsOnCurrent: newWrong,
    );

    // Fire and forget network call
    _submitAnswerAsync(activity.id, answer, state.pendingConfidence);
  }

  Future<void> _submitAnswerAsync(
    String activityId,
    String answer,
    double? confidence,
  ) async {
    try {
      final newMastery = await apiClient.submitAnswer(
        activityId: activityId,
        submittedAnswer: answer,
        confidence: confidence,
      );
      state = state.copyWith(mastery: newMastery, isOffline: false);

      // Online → drain offline queue
      await offlineQueue.syncQueue(onTokenExpired: _handleTokenExpired);
    } on AuthException {
      await _queueAndSignalExpiry(activityId, answer);
    } catch (_) {
      final token = await authService.getToken();
      await offlineQueue.enqueueAnswer(
        activityId: activityId,
        submittedAnswer: answer,
        authToken: token,
      );
      state = state.copyWith(isOffline: true);
    }
  }

  Future<void> _queueAndSignalExpiry(String activityId, String answer) async {
    final token = await authService.getToken();
    await offlineQueue.enqueueAnswer(
      activityId: activityId,
      submittedAnswer: answer,
      authToken: token,
    );
    _handleTokenExpired();
  }

  void _handleTokenExpired() {
    state = state.copyWith(isOffline: true, needsRelogin: true);
  }

  // ── Navigation ────────────────────────────────────────────────────────────

  /// Advance to the next activity, or mark session complete if at the end.
  void nextActivity() {
    if (state.isLastActivity) {
      state = state.copyWith(isComplete: true);
      return;
    }
    state = ActivitySessionState(
      activities:     state.activities,
      currentIndex:   state.currentIndex + 1,
      isLoading:      false,
      streak:         state.streak,
      bestStreak:     state.bestStreak,
      mastery:        state.mastery,
      initialMastery: state.initialMastery,
      correctCount:   state.correctCount,
      incorrectCount: state.incorrectCount,
      isAdaptive:     state.isAdaptive,
      agentReason:    state.agentReason,
      isOffline:      state.isOffline,
    );
  }

  /// Restart the session from the first activity.
  void restart() {
    state = ActivitySessionState(
      activities:     state.activities,
      currentIndex:   0,
      isLoading:      false,
      isAdaptive:     state.isAdaptive,
      agentReason:    state.agentReason,
    );
  }
}

// ── Provider ─────────────────────────────────────────────────────────────────

final activitySessionProvider =
    NotifierProvider<ActivitySessionNotifier, ActivitySessionState>(
  ActivitySessionNotifier.new,
);
