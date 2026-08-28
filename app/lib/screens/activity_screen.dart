import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../providers/activity_session_provider.dart';
import '../services/auth_service.dart';
import '../widgets/activity_runner.dart';
import '../widgets/feedback_panel.dart';
import 'login_screen.dart';
import 'tutor_screen.dart';

/// The single activity-flow screen.
///
/// Responsibilities:
///   - Load activities for [topicId] (or via Pedagogical Agent in adaptive mode)
///   - Render dual-track progress header
///   - Host the scrollable [ActivityRunner]
///   - Show metacognitive confidence check-in before submit
///   - Slide in [FeedbackPanel] after an answer is selected
///   - Surface struggle intervention after ≥2 wrong attempts
///   - Show expanded session recap on completion
class ActivityScreen extends ConsumerStatefulWidget {
  final String topicId;
  const ActivityScreen({super.key, this.topicId = 'loops'});

  @override
  ConsumerState<ActivityScreen> createState() => _ActivityScreenState();
}

class _ActivityScreenState extends ConsumerState<ActivityScreen> {
  bool _adaptive = true; // start in adaptive mode; user can toggle
  Timer? _struggleTimer;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _loadActivities());
  }

  @override
  void dispose() {
    _struggleTimer?.cancel();
    super.dispose();
  }

  Future<void> _loadActivities() async {
    try {
      if (_adaptive) {
        await ref.read(activitySessionProvider.notifier).fetchAdaptiveActivities();
      } else {
        await ref.read(activitySessionProvider.notifier).fetchActivities(widget.topicId);
      }
    } catch (e) {
      ref.read(activitySessionProvider.notifier).setError('Could not load activities:\n$e');
    }
  }

  void _switchMode() {
    setState(() => _adaptive = !_adaptive);
    _loadActivities();
  }

  @override
  Widget build(BuildContext context) {
    final session = ref.watch(activitySessionProvider);

    // ── Token expiry listener ──────────────────────────────────────────────
    ref.listen<ActivitySessionState>(activitySessionProvider, (_, next) {
      if (next.needsRelogin && mounted) {
        ref.read(activitySessionProvider.notifier).clearReloginFlag();
        showDialog(
          context: context,
          barrierDismissible: false,
          builder: (_) => AlertDialog(
            backgroundColor: const Color(0xFF141824),
            title: const Text('Session Expired',
                style: TextStyle(color: Colors.white)),
            content: const Text(
              'Your session has expired. Any offline answers are safely queued '
              'and will be submitted once you log back in.',
              style: TextStyle(color: Color(0xFF94A3B8)),
            ),
            actions: [
              TextButton(
                onPressed: () {
                  Navigator.of(context).pop();
                  Navigator.of(context).pushReplacement(
                    MaterialPageRoute(builder: (_) => const LoginScreen()),
                  );
                },
                child: const Text('Log In Again',
                    style: TextStyle(color: Color(0xFF6366F1))),
              ),
            ],
          ),
        );
      }

      // ── Struggle detection ─────────────────────────────────────────────
      if (next.shouldShowStruggle && mounted) {
        ref.read(activitySessionProvider.notifier).markStruggleShown();
        _showStruggleIntervention();
      }
    });

    // ── Loading ────────────────────────────────────────────────────────────
    if (session.isLoading) {
      return Scaffold(
        backgroundColor: const Color(0xFF0A0E1A),
        body: Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const CircularProgressIndicator(
                color: Color(0xFF6366F1),
                strokeWidth: 2.5,
              ),
              if (_adaptive) ...[
                const SizedBox(height: 20),
                const Text(
                  'Asking your tutor what to study next…',
                  style: TextStyle(color: Color(0xFF6B7280), fontSize: 13),
                ),
              ],
            ],
          ),
        ),
      );
    }

    // ── Error ──────────────────────────────────────────────────────────────
    if (session.error != null) {
      return Scaffold(
        backgroundColor: const Color(0xFF0A0E1A),
        body: Center(
          child: Padding(
            padding: const EdgeInsets.all(32),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(Icons.error_outline_rounded,
                    color: Color(0xFFEF4444), size: 48),
                const SizedBox(height: 16),
                Text(
                  session.error!,
                  textAlign: TextAlign.center,
                  style: const TextStyle(color: Color(0xFFEF4444), fontSize: 14),
                ),
                const SizedBox(height: 24),
                OutlinedButton.icon(
                  onPressed: _loadActivities,
                  icon: const Icon(Icons.refresh_rounded, size: 18),
                  label: const Text('Retry'),
                  style: OutlinedButton.styleFrom(
                    foregroundColor: const Color(0xFF6366F1),
                    side: const BorderSide(color: Color(0xFF6366F1)),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(10),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      );
    }

    // ── Session complete ───────────────────────────────────────────────────
    if (session.isComplete) {
      return _SessionRecap(
        session:   session,
        onRestart: () => ref.read(activitySessionProvider.notifier).restart(),
        onHome:    () => Navigator.of(context).pop(),
        onNextActivity: (topicId) {
          Navigator.of(context).pushReplacement(
            MaterialPageRoute(builder: (_) => ActivityScreen(topicId: topicId)),
          );
        },
      );
    }

    // ── Active session ─────────────────────────────────────────────────────
    final activity = session.currentActivity!;

    return Scaffold(
      backgroundColor: const Color(0xFF0A0E1A),
      body: SafeArea(
        child: Column(
          children: [
            _ProgressHeader(
              topicId:    activity.topicId,
              current:    session.currentIndex + 1,
              total:      session.activities.length,
              masteryProgress:    session.progress,
              completionProgress: session.completionProgress,
              streak:     session.streak,
              mastery:    session.mastery,
              isOffline:  session.isOffline,
              isAdaptive: session.isAdaptive,
              agentReason: session.agentReason,
              onToggleMode: _switchMode,
            ),

            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.fromLTRB(20, 20, 20, 0),
                child: AnimatedSwitcher(
                  duration: const Duration(milliseconds: 300),
                  child: KeyedSubtree(
                    key: ValueKey(activity.id),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        ActivityRunner(activity: activity),

                        // ── Confidence check-in ──────────────────────────
                        if (session.stagedAnswer != null)
                          _ConfidenceRow(
                            current: session.pendingConfidence,
                            onSelect: (v) => ref
                                .read(activitySessionProvider.notifier)
                                .submitStagedAnswer(v),
                          ),
                      ],
                    ),
                  ),
                ),
              ),
            ),

            AnimatedSwitcher(
              duration: const Duration(milliseconds: 380),
              transitionBuilder: (child, animation) => SlideTransition(
                position: Tween<Offset>(
                  begin: const Offset(0, 1),
                  end: Offset.zero,
                ).animate(CurvedAnimation(
                  parent: animation,
                  curve: Curves.easeOutCubic,
                )),
                child: child,
              ),
              child: session.isAnswered
                  ? FeedbackPanel(
                      key: ValueKey('feedback_${session.currentIndex}'),
                      isCorrect:   session.isCorrect,
                      explanation: activity.explanation,
                      isLast:      session.isLastActivity,
                      onNext: () =>
                          ref.read(activitySessionProvider.notifier).nextActivity(),
                    )
                  : const SizedBox.shrink(key: ValueKey('no_feedback')),
            ),
          ],
        ),
      ),
    );
  }

  void _showStruggleIntervention() {
    final activity = ref.read(activitySessionProvider).currentActivity;
    showModalBottomSheet(
      context: context,
      backgroundColor: const Color(0xFF141824),
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (_) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.fromLTRB(24, 16, 24, 24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Center(
                child: Container(
                  width: 36,
                  height: 4,
                  decoration: BoxDecoration(
                    color: const Color(0xFF374151),
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
              ),
              const SizedBox(height: 20),
              const Row(
                children: [
                  Text('🤔', style: TextStyle(fontSize: 22)),
                  SizedBox(width: 10),
                  Text(
                    'Looks like this one\'s tricky',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 16,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              const Text(
                "That's completely fine — let's try a different approach.",
                style: TextStyle(color: Color(0xFF9CA3AF), fontSize: 13),
              ),
              const SizedBox(height: 20),
              if (activity != null)
                _StruggleOption(
                  icon: Icons.lightbulb_outline_rounded,
                  label: 'Show me the explanation',
                  color: const Color(0xFFF59E0B),
                  onTap: () {
                    Navigator.pop(context);
                    showDialog(
                      context: context,
                      builder: (_) => AlertDialog(
                        backgroundColor: const Color(0xFF141824),
                        title: const Text('Hint',
                            style: TextStyle(color: Colors.white)),
                        content: Text(
                          activity.explanation,
                          style: const TextStyle(
                              color: Color(0xFF9CA3AF), fontSize: 13, height: 1.5),
                        ),
                        actions: [
                          TextButton(
                            onPressed: () => Navigator.pop(context),
                            child: const Text('Got it',
                                style: TextStyle(color: Color(0xFF6366F1))),
                          ),
                        ],
                      ),
                    );
                  },
                ),
              const SizedBox(height: 10),
              _StruggleOption(
                icon: Icons.skip_next_rounded,
                label: 'Skip this one for now',
                color: const Color(0xFF6366F1),
                onTap: () {
                  Navigator.pop(context);
                  ref.read(activitySessionProvider.notifier).nextActivity();
                },
              ),
              const SizedBox(height: 10),
              _StruggleOption(
                icon: Icons.chat_bubble_outline_rounded,
                label: 'Ask the tutor for help',
                color: const Color(0xFF3B82F6), // Blue
                onTap: () {
                  Navigator.pop(context);
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (_) => TutorScreen(
                        topicId: widget.topicId,
                        topicLabel: widget.topicId.replaceAll('-', ' ').toUpperCase(),
                      ),
                    ),
                  );
                },
              ),
              const SizedBox(height: 10),
              _StruggleOption(
                icon: Icons.self_improvement_rounded,
                label: 'Take a short break',
                color: const Color(0xFF10B981),
                onTap: () => Navigator.pop(context),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// ── Progress header ────────────────────────────────────────────────────────────

class _ProgressHeader extends StatelessWidget {
  final String topicId;
  final int current;
  final int total;
  final double masteryProgress;
  final double completionProgress;
  final int streak;
  final double mastery;
  final bool isOffline;
  final bool isAdaptive;
  final String? agentReason;
  final VoidCallback onToggleMode;

  const _ProgressHeader({
    required this.topicId,
    required this.current,
    required this.total,
    required this.masteryProgress,
    required this.completionProgress,
    required this.streak,
    required this.mastery,
    required this.isOffline,
    required this.isAdaptive,
    required this.agentReason,
    required this.onToggleMode,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(20, 16, 20, 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              // Topic label + adaptive badge
              Flexible(
                child: Row(
                  children: [
                    Flexible(
                      child: Text(
                        topicId.replaceAll('-', ' ').replaceAll('_', ' ').toUpperCase(),
                        style: const TextStyle(
                          color: Color(0xFF6366F1),
                          fontSize: 11,
                          fontWeight: FontWeight.w700,
                          letterSpacing: 1.6,
                        ),
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                    const SizedBox(width: 6),
                    if (isAdaptive)
                      GestureDetector(
                        onTap: onToggleMode,
                        child: Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 6, vertical: 2),
                          decoration: BoxDecoration(
                            color: const Color(0xFF6366F1).withValues(alpha: 0.15),
                            borderRadius: BorderRadius.circular(6),
                            border: Border.all(
                              color: const Color(0xFF6366F1).withValues(alpha: 0.4),
                            ),
                          ),
                          child: const Text(
                            'ADAPTIVE',
                            style: TextStyle(
                              color: Color(0xFF6366F1),
                              fontSize: 8,
                              fontWeight: FontWeight.w800,
                              letterSpacing: 0.8,
                            ),
                          ),
                        ),
                      )
                    else
                      GestureDetector(
                        onTap: onToggleMode,
                        child: Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 6, vertical: 2),
                          decoration: BoxDecoration(
                            color: const Color(0xFF374151).withValues(alpha: 0.5),
                            borderRadius: BorderRadius.circular(6),
                          ),
                          child: const Text(
                            'LINEAR',
                            style: TextStyle(
                              color: Color(0xFF6B7280),
                              fontSize: 8,
                              fontWeight: FontWeight.w700,
                              letterSpacing: 0.8,
                            ),
                          ),
                        ),
                      ),
                    IconButton(
                      icon: const Icon(Icons.logout, size: 16, color: Color(0xFF9CA3AF)),
                      padding: EdgeInsets.zero,
                      constraints: const BoxConstraints(),
                      onPressed: () async {
                        await authService.clearToken();
                        if (context.mounted) {
                          Navigator.of(context).pushReplacement(
                            MaterialPageRoute(builder: (_) => const LoginScreen()),
                          );
                        }
                      },
                    ),
                  ],
                ),
              ),
              // Stats
              Row(
                children: [
                  _StatChip(
                    icon: '🔥',
                    value: '$streak',
                    color: streak > 0
                        ? const Color(0xFFF97316)
                        : const Color(0xFF4B5563),
                  ),
                  const SizedBox(width: 8),
                  _StatChip(
                    icon: '🎓',
                    value: '${(mastery * 100).toInt()}%',
                    color: mastery > 0
                        ? const Color(0xFF10B981)
                        : const Color(0xFF4B5563),
                  ),
                  if (isOffline) ...[
                    const SizedBox(width: 8),
                    _StatChip(
                      icon: '☁️',
                      value: 'Offline',
                      color: const Color(0xFFFBBF24),
                    ),
                  ],
                  const SizedBox(width: 10),
                  Container(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                    decoration: BoxDecoration(
                      color: const Color(0xFF1F2937),
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Text(
                      '$current / $total',
                      style: const TextStyle(
                        color: Color(0xFF9CA3AF),
                        fontSize: 12,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),

          // Agent reason subtitle
          if (isAdaptive && agentReason != null) ...[
            const SizedBox(height: 4),
            Text(
              agentReason!,
              style: const TextStyle(
                color: Color(0xFF4B5563),
                fontSize: 10,
                fontStyle: FontStyle.italic,
              ),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
          ],

          const SizedBox(height: 10),

          // ── Dual-track progress bars ────────────────────────────────────
          // Top: mastery delta (what actually matters)
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  const Text('Mastery gained',
                      style: TextStyle(
                          color: Color(0xFF4B5563), fontSize: 9)),
                  const Spacer(),
                  Text('Questions done',
                      style: TextStyle(
                          color: Colors.white.withValues(alpha: 0.15),
                          fontSize: 9)),
                ],
              ),
              const SizedBox(height: 3),
              Stack(
                children: [
                  // Completion track (background, subtle)
                  ClipRRect(
                    borderRadius: BorderRadius.circular(4),
                    child: LinearProgressIndicator(
                      value: completionProgress,
                      backgroundColor: const Color(0xFF1F2937),
                      valueColor: AlwaysStoppedAnimation(
                        const Color(0xFF374151).withValues(alpha: 0.6),
                      ),
                      minHeight: 5,
                    ),
                  ),
                  // Mastery track (foreground, vivid)
                  ClipRRect(
                    borderRadius: BorderRadius.circular(4),
                    child: TweenAnimationBuilder<double>(
                      tween: Tween(begin: 0, end: masteryProgress),
                      duration: const Duration(milliseconds: 450),
                      curve: Curves.easeOutCubic,
                      builder: (_, value, _) => LinearProgressIndicator(
                        value: value,
                        backgroundColor: Colors.transparent,
                        valueColor: const AlwaysStoppedAnimation(Color(0xFF6366F1)),
                        minHeight: 5,
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ],
      ),
    );
  }
}

// ── Confidence check-in ────────────────────────────────────────────────────

class _ConfidenceRow extends StatelessWidget {
  final double? current;
  final void Function(double) onSelect;

  const _ConfidenceRow({required this.current, required this.onSelect});

  static const _levels = [0.25, 0.5, 0.75, 1.0];
  static const _labels = ['Guessing', 'Unsure', 'Pretty sure', 'Certain'];
  static const _emojis = ['🤔', '🙂', '😊', '💪'];

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'How sure are you?',
            style: TextStyle(
              color: Color(0xFF6B7280),
              fontSize: 12,
              fontWeight: FontWeight.w500,
            ),
          ),
          const SizedBox(height: 8),
          Row(
            children: List.generate(_levels.length, (i) {
              final selected = current != null &&
                  (current! - _levels[i]).abs() < 0.01;
              return Expanded(
                child: GestureDetector(
                  onTap: () => onSelect(_levels[i]),
                  child: AnimatedContainer(
                    duration: const Duration(milliseconds: 180),
                    margin: EdgeInsets.only(right: i < _levels.length - 1 ? 6 : 0),
                    padding: const EdgeInsets.symmetric(vertical: 8),
                    decoration: BoxDecoration(
                      color: selected
                          ? const Color(0xFF6366F1).withValues(alpha: 0.15)
                          : const Color(0xFF1F2937),
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(
                        color: selected
                            ? const Color(0xFF6366F1)
                            : const Color(0xFF374151),
                      ),
                    ),
                    child: Column(
                      children: [
                        Text(_emojis[i],
                            style: const TextStyle(fontSize: 14)),
                        const SizedBox(height: 2),
                        Text(
                          _labels[i],
                          style: TextStyle(
                            color: selected
                                ? const Color(0xFF6366F1)
                                : const Color(0xFF4B5563),
                            fontSize: 9,
                            fontWeight: selected
                                ? FontWeight.w600
                                : FontWeight.w400,
                          ),
                          textAlign: TextAlign.center,
                        ),
                      ],
                    ),
                  ),
                ),
              );
            }),
          ),
        ],
      ),
    );
  }
}

// ── Session recap ──────────────────────────────────────────────────────────────

class _SessionRecap extends StatelessWidget {
  final ActivitySessionState session;
  final VoidCallback onRestart;
  final VoidCallback onHome;
  final void Function(String) onNextActivity;

  const _SessionRecap({
    required this.session,
    required this.onRestart,
    required this.onHome,
    required this.onNextActivity,
  });

  @override
  Widget build(BuildContext context) {
    final masteryDelta = session.mastery - session.initialMastery;
    final total = session.correctCount + session.incorrectCount;
    final pct   = total == 0 ? 0 : (session.correctCount / total * 100).toInt();

    return Scaffold(
      backgroundColor: const Color(0xFF0A0E1A),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(28),
          child: Column(
            children: [
              const SizedBox(height: 20),

              // Trophy
              Container(
                width: 88,
                height: 88,
                decoration: BoxDecoration(
                  color: const Color(0xFF6366F1).withValues(alpha: 0.12),
                  shape: BoxShape.circle,
                  border: Border.all(
                    color: const Color(0xFF6366F1).withValues(alpha: 0.3),
                    width: 1.5,
                  ),
                ),
                child: const Icon(Icons.emoji_events_rounded,
                    color: Color(0xFF6366F1), size: 44),
              ),
              const SizedBox(height: 24),

              const Text(
                'Session Complete!',
                style: TextStyle(
                  color: Color(0xFFF9FAFB),
                  fontSize: 24,
                  fontWeight: FontWeight.w700,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                session.isAdaptive
                    ? 'Adaptive session on ${session.currentActivity?.topicId ?? "your current topic"}'
                    : 'You worked through all ${session.activities.length} activities.',
                textAlign: TextAlign.center,
                style: const TextStyle(
                  color: Color(0xFF9CA3AF),
                  fontSize: 14,
                  height: 1.5,
                ),
              ),
              const SizedBox(height: 28),

              // Stats grid
              GridView.count(
                crossAxisCount: 2,
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                crossAxisSpacing: 12,
                mainAxisSpacing: 12,
                childAspectRatio: 2.2,
                children: [
                  _RecapStat(
                      emoji: '✅',
                      label: 'Correct',
                      value: '${session.correctCount}'),
                  _RecapStat(
                      emoji: '❌',
                      label: 'Incorrect',
                      value: '${session.incorrectCount}'),
                  _RecapStat(
                      emoji: '🎯',
                      label: 'Accuracy',
                      value: '$pct%'),
                  _RecapStat(
                      emoji: '🔥',
                      label: 'Best streak',
                      value: '${session.bestStreak}'),
                ],
              ),
              const SizedBox(height: 16),

              // Mastery delta chip
              Container(
                width: double.infinity,
                padding:
                    const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
                decoration: BoxDecoration(
                  color: const Color(0xFF10B981).withValues(alpha: 0.08),
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(
                    color: const Color(0xFF10B981).withValues(alpha: 0.3),
                  ),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Text('📈', style: TextStyle(fontSize: 18)),
                    const SizedBox(width: 10),
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text('Mastery',
                            style: TextStyle(
                                color: Color(0xFF6B7280), fontSize: 11)),
                        Text(
                          masteryDelta > 0
                              ? '+${(masteryDelta * 100).toInt()}%  →  ${(session.mastery * 100).toInt()}% total'
                              : '${(session.mastery * 100).toInt()}% total',
                          style: const TextStyle(
                            color: Color(0xFF10B981),
                            fontSize: 15,
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 32),

              if (session.nextRecommendation != null) ...[
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    color: const Color(0xFF1E293B),
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: const Color(0xFF334155)),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Container(
                            padding: const EdgeInsets.all(8),
                            decoration: BoxDecoration(
                              color: const Color(0xFF6366F1).withValues(alpha: 0.2),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: const Icon(Icons.psychology_rounded,
                                color: Color(0xFF818CF8), size: 20),
                          ),
                          const SizedBox(width: 12),
                          const Text(
                            'Up Next from your Tutor',
                            style: TextStyle(
                              color: Color(0xFFE2E8F0),
                              fontSize: 15,
                              fontWeight: FontWeight.w700,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 16),
                      Text(
                        'Recommended Topic: ${session.nextRecommendation!.topicId.replaceAll('-', ' ').toUpperCase()}',
                        style: const TextStyle(
                          color: Color(0xFF94A3B8),
                          fontSize: 13,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        session.nextRecommendation!.reason,
                        style: const TextStyle(
                          color: Color(0xFFCBD5E1),
                          fontSize: 14,
                          height: 1.5,
                        ),
                      ),
                      const SizedBox(height: 20),
                      SizedBox(
                        width: double.infinity,
                        child: FilledButton.icon(
                          onPressed: () => onNextActivity(session.nextRecommendation!.topicId),
                          icon: const Icon(Icons.arrow_forward_rounded, size: 18),
                          label: const Text('Start Recommended Topic',
                              style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600)),
                          style: FilledButton.styleFrom(
                            backgroundColor: const Color(0xFF4F46E5), // Indigo
                            padding: const EdgeInsets.symmetric(vertical: 14),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(10),
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 24),
              ],

              // Buttons
              SizedBox(
                width: double.infinity,
                child: FilledButton.icon(
                  onPressed: onRestart,
                  icon: const Icon(Icons.replay_rounded, size: 18),
                  label: const Text('Practice Again',
                      style: TextStyle(
                          fontSize: 15, fontWeight: FontWeight.w600)),
                  style: FilledButton.styleFrom(
                    backgroundColor: const Color(0xFF6366F1),
                    padding: const EdgeInsets.symmetric(vertical: 15),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 12),
              SizedBox(
                width: double.infinity,
                child: OutlinedButton.icon(
                  onPressed: onHome,
                  icon: const Icon(Icons.home_rounded, size: 18),
                  label: const Text('Return Home',
                      style: TextStyle(
                          fontSize: 15, fontWeight: FontWeight.w600)),
                  style: OutlinedButton.styleFrom(
                    foregroundColor: const Color(0xFF6B7280),
                    side: const BorderSide(color: Color(0xFF374151)),
                    padding: const EdgeInsets.symmetric(vertical: 15),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _RecapStat extends StatelessWidget {
  final String emoji;
  final String label;
  final String value;

  const _RecapStat(
      {required this.emoji, required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
      decoration: BoxDecoration(
        color: const Color(0xFF141824),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFF1F2937)),
      ),
      child: Row(
        children: [
          Text(emoji, style: const TextStyle(fontSize: 18)),
          const SizedBox(width: 10),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text(label,
                  style: const TextStyle(
                      color: Color(0xFF4B5563), fontSize: 10)),
              Text(value,
                  style: const TextStyle(
                    color: Color(0xFFF3F4F6),
                    fontSize: 17,
                    fontWeight: FontWeight.w700,
                  )),
            ],
          ),
        ],
      ),
    );
  }
}

// ── Stat chip ─────────────────────────────────────────────────────────────────

class _StatChip extends StatelessWidget {
  final String icon;
  final String value;
  final Color color;

  const _StatChip({required this.icon, required this.value, required this.color});

  @override
  Widget build(BuildContext context) {
    return AnimatedContainer(
      duration: const Duration(milliseconds: 300),
      curve: Curves.easeOut,
      padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 4),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color.withValues(alpha: 0.35)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(icon, style: const TextStyle(fontSize: 12)),
          const SizedBox(width: 4),
          AnimatedSwitcher(
            duration: const Duration(milliseconds: 250),
            transitionBuilder: (child, anim) =>
                ScaleTransition(scale: anim, child: child),
            child: Text(
              value,
              key: ValueKey(value),
              style: TextStyle(
                color: color,
                fontSize: 12,
                fontWeight: FontWeight.w700,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

// ── Struggle intervention option ─────────────────────────────────────────────

class _StruggleOption extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color color;
  final VoidCallback onTap;

  const _StruggleOption({
    required this.icon,
    required this.label,
    required this.color,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: onTap,
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
          decoration: BoxDecoration(
            color: color.withValues(alpha: 0.08),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: color.withValues(alpha: 0.2)),
          ),
          child: Row(
            children: [
              Icon(icon, color: color, size: 20),
              const SizedBox(width: 12),
              Text(
                label,
                style: TextStyle(
                  color: color,
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
