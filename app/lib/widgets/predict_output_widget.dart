import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../models/activity.dart';
import '../providers/activity_session_provider.dart';
import 'code_block.dart';
import 'difficulty_badge.dart';
import 'option_card.dart';

/// Renders a single predict_output activity.
///
/// Layout:
///   1. Difficulty badge
///   2. Prompt text
///   3. Code block (when code_snippet is non-null)
///   4. Tappable option cards
///
/// All interaction is delegated upward to [activitySessionProvider].
/// Does not own any local state.
class PredictOutputWidget extends ConsumerWidget {
  final Activity activity;

  const PredictOutputWidget({super.key, required this.activity});

  static const _labels = ['A', 'B', 'C', 'D', 'E', 'F'];

  OptionState _stateFor(String option, ActivitySessionState session) {
    if (session.isAnswered) {
      if (option == activity.correctAnswer) return OptionState.correct;
      if (option == session.selectedAnswer) return OptionState.incorrect;
      return OptionState.idle;
    }
    if (option == session.stagedAnswer) return OptionState.staged;
    return OptionState.idle;
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final session = ref.watch(activitySessionProvider);
    final options = activity.options ?? [];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // ── Difficulty badge ─────────────────────────────────────────────
        DifficultyBadge(difficulty: activity.difficulty),
        const SizedBox(height: 16),

        // ── Prompt ───────────────────────────────────────────────────────
        Text(
          activity.promptText,
          style: const TextStyle(
            color: Color(0xFFF3F4F6),
            fontSize: 16,
            height: 1.6,
            fontWeight: FontWeight.w500,
          ),
        ),

        // ── Code snippet ─────────────────────────────────────────────────
        if (activity.codeSnippet != null) ...[
          const SizedBox(height: 16),
          CodeBlock(code: activity.codeSnippet!),
        ],

        const SizedBox(height: 22),

        // ── Options ──────────────────────────────────────────────────────
        ...options.asMap().entries.map((entry) {
          final idx = entry.key;
          final opt = entry.value;
          return OptionCard(
            label: _labels[idx.clamp(0, _labels.length - 1)],
            text: opt,
            state: _stateFor(opt, session),
            onTap: () =>
                ref.read(activitySessionProvider.notifier).stageAnswer(opt),
          );
        }),

        // Bottom padding so feedback panel doesn't obscure last option
        const SizedBox(height: 24),
      ],
    );
  }
}

