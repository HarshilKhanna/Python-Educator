import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../providers/activity_session_provider.dart';
import '../services/auth_service.dart';
import '../widgets/activity_runner.dart';
import '../widgets/feedback_panel.dart';
import 'login_screen.dart';

/// The single activity-flow screen.
///
/// Responsibilities:
///   - Load activities for [topicId] from the backend on first build
///   - Render progress header
///   - Host the scrollable [ActivityRunner]
///   - Slide in [FeedbackPanel] after an answer is selected
///   - Show a completion card when the session ends
class ActivityScreen extends ConsumerStatefulWidget {
  final String topicId;
  const ActivityScreen({super.key, this.topicId = 'loops'});

  @override
  ConsumerState<ActivityScreen> createState() => _ActivityScreenState();
}

class _ActivityScreenState extends ConsumerState<ActivityScreen> {
  @override
  void initState() {
    super.initState();
    // Defer until after first frame so the provider is fully mounted.
    WidgetsBinding.instance.addPostFrameCallback((_) => _loadActivities());
  }

  Future<void> _loadActivities() async {
    try {
      await ref
          .read(activitySessionProvider.notifier)
          .fetchActivities(widget.topicId);
    } catch (e) {
      ref
          .read(activitySessionProvider.notifier)
          .setError('Could not load activities:\n$e');
    }
  }


  @override
  Widget build(BuildContext context) {
    final session = ref.watch(activitySessionProvider);

    // Listen for token-expiry signal from offline queue sync
    ref.listen<ActivitySessionState>(activitySessionProvider, (_, next) {
      if (next.needsRelogin && mounted) {
        // Clear the flag so the listener doesn't fire again
        ref.read(activitySessionProvider.notifier).clearReloginFlag();
        // Show re-login prompt — queued answers are safe
        showDialog(
          context: context,
          barrierDismissible: false,
          builder: (_) => AlertDialog(
            backgroundColor: const Color(0xFF141824),
            title: const Text(
              'Session Expired',
              style: TextStyle(color: Colors.white),
            ),
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
    });

    if (session.isLoading) {
      return const Scaffold(
        backgroundColor: Color(0xFF0A0E1A),
        body: Center(
          child: CircularProgressIndicator(
            color: Color(0xFF6366F1),
            strokeWidth: 2.5,
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
            child: Text(
              session.error!,
              textAlign: TextAlign.center,
              style: const TextStyle(color: Color(0xFFEF4444), fontSize: 14),
            ),
          ),
        ),
      );
    }

    // ── Session complete ───────────────────────────────────────────────────
    if (session.isComplete) {
      return _CompletionScreen(
        total: session.activities.length,
        mastery: session.mastery,
        onRestart: () =>
            ref.read(activitySessionProvider.notifier).restart(),
      );
    }

    // ── Active session ─────────────────────────────────────────────────────
    final activity = session.currentActivity!;

    return Scaffold(
      backgroundColor: const Color(0xFF0A0E1A),
      body: SafeArea(
        child: Column(
          children: [
            // Progress header
            _ProgressHeader(
              topicId: activity.topicId,
              current: session.currentIndex + 1,
              total: session.activities.length,
              progress: session.progress,
              streak: session.streak,
              mastery: session.mastery,
              isOffline: session.isOffline,
            ),

            // Scrollable activity content
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.fromLTRB(20, 20, 20, 0),
                child: AnimatedSwitcher(
                  duration: const Duration(milliseconds: 300),
                  child: KeyedSubtree(
                    key: ValueKey(activity.id),
                    child: ActivityRunner(activity: activity),
                  ),
                ),
              ),
            ),

            // Feedback panel — slides in after answering
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
                      isCorrect: session.isCorrect,
                      explanation: activity.explanation,
                      isLast: session.isLastActivity,
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
}

// ── Progress header ───────────────────────────────────────────────────────────

class _ProgressHeader extends StatelessWidget {
  final String topicId;
  final int current;
  final int total;
  final double progress;
  final int streak;
  final double mastery;
  final bool isOffline;

  const _ProgressHeader({
    required this.topicId,
    required this.current,
    required this.total,
    required this.progress,
    required this.streak,
    required this.mastery,
    required this.isOffline,
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
              // Topic label and Logout
              Row(
                children: [
                  Text(
                    topicId.replaceAll('_', ' ').toUpperCase(),
                    style: const TextStyle(
                      color: Color(0xFF6366F1),
                      fontSize: 11,
                      fontWeight: FontWeight.w700,
                      letterSpacing: 1.6,
                    ),
                  ),
                  const SizedBox(width: 8),
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
              // Stats: streak + score + counter
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
                        ? const Color(0xFF10B981) // Emerald green
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
                  // Progress counter pill
                  Container(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                    decoration: BoxDecoration(
                      color: const Color(0xFF1F2937),
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Text(
                      '$current / $total',
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
          const SizedBox(height: 10),
          // Progress bar
          ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: TweenAnimationBuilder<double>(
              tween: Tween(begin: 0, end: progress),
              duration: const Duration(milliseconds: 450),
              curve: Curves.easeOutCubic,
              builder: (_, value, _) => LinearProgressIndicator(
                value: value,
                backgroundColor: const Color(0xFF1F2937),
                valueColor:
                    const AlwaysStoppedAnimation(Color(0xFF6366F1)),
                minHeight: 5,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

// ── Completion screen ─────────────────────────────────────────────────────────

class _CompletionScreen extends StatelessWidget {
  final int total;
  final double mastery;
  final VoidCallback onRestart;

  const _CompletionScreen({
    required this.total,
    required this.mastery,
    required this.onRestart,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A0E1A),
      body: SafeArea(
        child: Center(
          child: Padding(
            padding: const EdgeInsets.all(32),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                // Trophy icon
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
                  child: const Icon(
                    Icons.emoji_events_rounded,
                    color: Color(0xFF6366F1),
                    size: 44,
                  ),
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
                const SizedBox(height: 10),
                Text(
                  'You worked through all $total activities.',
                  textAlign: TextAlign.center,
                  style: const TextStyle(
                    color: Color(0xFF9CA3AF),
                    fontSize: 15,
                    height: 1.5,
                  ),
                ),
                const SizedBox(height: 16),
                // Final score chip
                Container(
                  padding: const EdgeInsets.symmetric(
                      horizontal: 20, vertical: 10),
                  decoration: BoxDecoration(
                    color: const Color(0xFFFBBF24).withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(24),
                    border: Border.all(
                      color: const Color(0xFFFBBF24).withValues(alpha: 0.35),
                    ),
                  ),
                  child: Text(
                    '🎓 Final Mastery: ${(mastery * 100).toInt()}%',
                    style: const TextStyle(
                      color: Color(0xFF10B981),
                      fontSize: 16,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ),
                const SizedBox(height: 36),
                SizedBox(
                  width: double.infinity,
                  child: FilledButton.icon(
                    onPressed: onRestart,
                    icon: const Icon(Icons.replay_rounded, size: 18),
                    label: const Text(
                      'Practice Again',
                      style: TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    style: FilledButton.styleFrom(
                      backgroundColor: const Color(0xFF6366F1),
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
      ),
    );
  }
}

// ── Stat chip (streak / score) ────────────────────────────────────────────────

class _StatChip extends StatelessWidget {
  final String icon;
  final String value;
  final Color color;

  const _StatChip({
    required this.icon,
    required this.value,
    required this.color,
  });

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
            transitionBuilder: (child, anim) => ScaleTransition(
              scale: anim,
              child: child,
            ),
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
