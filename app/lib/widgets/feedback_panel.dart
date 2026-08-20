import 'package:flutter/material.dart';

/// Slides up from the bottom after an answer is selected.
/// Shows correct/incorrect verdict, explanation text, and the Next button.
class FeedbackPanel extends StatelessWidget {
  final bool isCorrect;
  final String explanation;
  final bool isLast;
  final VoidCallback onNext;

  const FeedbackPanel({
    super.key,
    required this.isCorrect,
    required this.explanation,
    required this.isLast,
    required this.onNext,
  });

  static const _correct = Color(0xFF22C55E);
  static const _incorrect = Color(0xFFEF4444);

  @override
  Widget build(BuildContext context) {
    final accent = isCorrect ? _correct : _incorrect;
    final bg = isCorrect ? const Color(0xFF0A2119) : const Color(0xFF220F0F);

    return Container(
      padding: const EdgeInsets.fromLTRB(20, 20, 20, 28),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: const BorderRadius.only(
          topLeft: Radius.circular(24),
          topRight: Radius.circular(24),
        ),
        border: Border(
          top: BorderSide(color: accent.withValues(alpha: 0.45), width: 1.5),
        ),
        boxShadow: [
          BoxShadow(
            color: accent.withValues(alpha: 0.08),
            blurRadius: 24,
            spreadRadius: 0,
            offset: const Offset(0, -4),
          ),
        ],
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // ── Verdict row ────────────────────────────────────────────────
          Row(
            children: [
              Icon(
                isCorrect
                    ? Icons.check_circle_rounded
                    : Icons.cancel_rounded,
                color: accent,
                size: 22,
              ),
              const SizedBox(width: 8),
              Text(
                isCorrect ? 'Correct!' : 'Not quite',
                style: TextStyle(
                  color: accent,
                  fontSize: 17,
                  fontWeight: FontWeight.w700,
                  letterSpacing: 0.2,
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          // ── Explanation ────────────────────────────────────────────────
          Text(
            explanation,
            style: const TextStyle(
              color: Color(0xFFD1D5DB),
              fontSize: 14,
              height: 1.6,
            ),
          ),
          const SizedBox(height: 20),
          // ── Next / Finish button ───────────────────────────────────────
          SizedBox(
            width: double.infinity,
            child: FilledButton(
              onPressed: onNext,
              style: FilledButton.styleFrom(
                backgroundColor: accent,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 15),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                elevation: 0,
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(
                    isLast ? 'Finish' : 'Next',
                    style: const TextStyle(
                      fontSize: 15,
                      fontWeight: FontWeight.w600,
                      letterSpacing: 0.3,
                    ),
                  ),
                  if (!isLast) ...[
                    const SizedBox(width: 6),
                    const Icon(Icons.arrow_forward_rounded, size: 18),
                  ],
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
