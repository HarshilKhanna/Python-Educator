import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/activity.dart';
import '../services/api_client.dart';
import '../services/offline_queue.dart';

// ── State ────────────────────────────────────────────────────────────────────

/// Immutable snapshot of the active practice session.
class ActivitySessionState {
  final List<Activity> activities;
  final int currentIndex;
  final String? selectedAnswer; // null ⟹ not yet answered
  final bool isLoading;
  final String? error;
  final bool isComplete; // true after the user clicks "Finish" on the last activity

  /// Consecutive correct answers in this session.
  final int streak;

  /// Mastery value returned from the backend (0.0 to 1.0)
  final double mastery;
  
  /// True if the last submission is queued offline
  final bool isOffline;

  const ActivitySessionState({
    this.activities = const [],
    this.currentIndex = 0,
    this.selectedAnswer,
    this.isLoading = true,
    this.error,
    this.isComplete = false,
    this.streak = 0,
    this.mastery = 0.0,
    this.isOffline = false,
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

  double get progress =>
      activities.isEmpty ? 0 : (currentIndex + 1) / activities.length;

  // ── Copy helper ────────────────────────────────────────────────────────────

  ActivitySessionState copyWith({
    List<Activity>? activities,
    int? currentIndex,
    Object? selectedAnswer = _sentinel,
    bool? isLoading,
    String? error,
    bool? isComplete,
    int? streak,
    double? mastery,
    bool? isOffline,
  }) {
    return ActivitySessionState(
      activities: activities ?? this.activities,
      currentIndex: currentIndex ?? this.currentIndex,
      selectedAnswer:
          selectedAnswer == _sentinel ? this.selectedAnswer : selectedAnswer as String?,
      isLoading: isLoading ?? this.isLoading,
      error: error ?? this.error,
      isComplete: isComplete ?? this.isComplete,
      streak: streak ?? this.streak,
      mastery: mastery ?? this.mastery,
      isOffline: isOffline ?? this.isOffline,
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

  /// Fetch activities from backend API
  Future<void> fetchActivities(String topicId) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final activities = await apiClient.fetchActivities(topicId);
      
      // Also try to sync any offline queue when we successfully connect
      await offlineQueue.syncQueue();
      
      state = ActivitySessionState(
        activities: activities,
        currentIndex: 0,
        isLoading: false,
      );
    } catch (e) {
      state = ActivitySessionState(isLoading: false, error: 'Failed to load activities: $e');
    }
  }

  /// Surfaced to the UI on asset-loading failure.
  void setError(String message) {
    state = ActivitySessionState(isLoading: false, error: message);
  }

  /// Lock-once: only the first tap registers.
  /// Submits the answer optimistically and updates mastery from backend async.
  void selectAnswer(String answer) {
    if (state.isAnswered) return;
    
    final activity = state.currentActivity;
    if (activity == null) return;
    
    final correct = answer == activity.correctAnswer;
    final newStreak = correct ? state.streak + 1 : 0;
    
    // Optimistic UI update
    state = state.copyWith(
      selectedAnswer: answer,
      streak: newStreak,
    );
    
    // Fire and forget network call
    _submitAnswerAsync(activity.id, answer);
  }

  Future<void> _submitAnswerAsync(String activityId, String answer) async {
    try {
      final newMastery = await apiClient.submitAnswer(
        studentId: 'student_123', // Hardcoded for prototype
        activityId: activityId,
        submittedAnswer: answer,
      );
      state = state.copyWith(mastery: newMastery, isOffline: false);
      
      // We are online, maybe sync queue
      await offlineQueue.syncQueue();
    } catch (e) {
      // Offline or network error -> queue it
      await offlineQueue.enqueueAnswer(
        studentId: 'student_123',
        activityId: activityId,
        submittedAnswer: answer,
      );
      state = state.copyWith(isOffline: true);
    }
  }

  /// Advance to the next activity, or mark session complete if at the end.
  void nextActivity() {
    if (state.isLastActivity) {
      state = state.copyWith(isComplete: true);
      return;
    }
    state = ActivitySessionState(
      activities: state.activities,
      currentIndex: state.currentIndex + 1,
      isLoading: false,
    );
  }

  /// Restart the session from the first activity (resets streak and mastery).
  void restart() {
    state = ActivitySessionState(
      activities: state.activities,
      currentIndex: 0,
      isLoading: false,
      streak: 0,
      mastery: 0.0,
      isOffline: false,
    );
  }
}

// ── Provider ─────────────────────────────────────────────────────────────────

final activitySessionProvider =
    NotifierProvider<ActivitySessionNotifier, ActivitySessionState>(
  ActivitySessionNotifier.new,
);
