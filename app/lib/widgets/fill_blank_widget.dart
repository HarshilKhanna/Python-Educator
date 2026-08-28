import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../models/activity.dart';
import '../providers/activity_session_provider.dart';
import 'code_block.dart';
import 'difficulty_badge.dart';

class FillBlankWidget extends ConsumerStatefulWidget {
  final Activity activity;

  const FillBlankWidget({super.key, required this.activity});

  @override
  ConsumerState<FillBlankWidget> createState() => _FillBlankWidgetState();
}

class _FillBlankWidgetState extends ConsumerState<FillBlankWidget> {
  final _controller = TextEditingController();
  final _focusNode = FocusNode();

  @override
  void dispose() {
    _controller.dispose();
    _focusNode.dispose();
    super.dispose();
  }

  void _submit() {
    final text = _controller.text.trim();
    if (text.isEmpty) return;
    ref.read(activitySessionProvider.notifier).stageAnswer(text);
    _focusNode.unfocus();
  }

  @override
  Widget build(BuildContext context) {
    final session = ref.watch(activitySessionProvider);
    final isAnswered = session.isAnswered;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        DifficultyBadge(difficulty: widget.activity.difficulty),
        const SizedBox(height: 16),
        Text(
          widget.activity.promptText,
          style: const TextStyle(
            color: Color(0xFFF3F4F6),
            fontSize: 16,
            height: 1.6,
            fontWeight: FontWeight.w500,
          ),
        ),
        if (widget.activity.codeSnippet != null) ...[
          const SizedBox(height: 16),
          CodeBlock(code: widget.activity.codeSnippet!),
        ],
        const SizedBox(height: 24),
        TextField(
          controller: _controller,
          focusNode: _focusNode,
          enabled: !isAnswered && session.stagedAnswer == null,
          style: const TextStyle(
            color: Color(0xFFE6EDF3),
            fontFamily: 'monospace',
            fontSize: 15,
          ),
          decoration: InputDecoration(
            hintText: 'Type your answer here...',
            hintStyle: TextStyle(
              color: const Color(0xFF6E7681).withValues(alpha: 0.8),
              fontFamily: 'monospace',
            ),
            filled: true,
            fillColor: const Color(0xFF141824),
            contentPadding:
                const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: Color(0xFF2D3347), width: 1.5),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: Color(0xFF2D3347), width: 1.5),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: Color(0xFF6366F1), width: 2),
            ),
            suffixIcon: IconButton(
              icon: const Icon(Icons.send_rounded),
              color: const Color(0xFF6366F1),
              onPressed: (isAnswered || session.stagedAnswer != null) ? null : _submit,
            ),
          ),
          onSubmitted: (_) {
            if (!isAnswered && session.stagedAnswer == null) _submit();
          },
        ),
        const SizedBox(height: 24),
      ],
    );
  }
}
