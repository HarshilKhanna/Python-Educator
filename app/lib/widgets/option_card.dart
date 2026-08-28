import 'package:flutter/material.dart';

/// Visual state of a single option card.
enum OptionState {
  idle,      // not yet answered
  staged,    // selected by user, awaiting confidence check
  correct,   // this option is the right answer (shown after answering)
  incorrect, // learner picked this — and it is wrong
}

/// A tappable answer-choice card.
/// Animates between [OptionState] values to give instant visual feedback.
class OptionCard extends StatelessWidget {
  final String label; // A, B, C, D
  final String text;
  final OptionState state;
  final VoidCallback? onTap;

  const OptionCard({
    super.key,
    required this.label,
    required this.text,
    required this.state,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final c = _colors();
    return AnimatedContainer(
      duration: const Duration(milliseconds: 220),
      curve: Curves.easeOut,
      margin: const EdgeInsets.only(bottom: 10),
      decoration: BoxDecoration(
        color: c.bg,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: c.border, width: 1.5),
      ),
      child: Material(
        color: Colors.transparent,
        borderRadius: BorderRadius.circular(12),
        child: InkWell(
          borderRadius: BorderRadius.circular(12),
          onTap: (state == OptionState.idle || state == OptionState.staged) ? onTap : null,
          splashColor: const Color(0xFF6366F1).withValues(alpha: 0.15),
          highlightColor: Colors.transparent,
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 13),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Label badge
                AnimatedContainer(
                  duration: const Duration(milliseconds: 220),
                  width: 28,
                  height: 28,
                  decoration: BoxDecoration(
                    color: c.badgeBg,
                    borderRadius: BorderRadius.circular(7),
                  ),
                  alignment: Alignment.center,
                  child: Text(
                    label,
                    style: TextStyle(
                      color: c.badgeText,
                      fontWeight: FontWeight.w700,
                      fontSize: 12,
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                // Option text
                Expanded(
                  child: Text(
                    text,
                    style: TextStyle(
                      color: c.text,
                      fontFamily: 'monospace',
                      fontSize: 13.5,
                      height: 1.55,
                    ),
                  ),
                ),
                // State icon
                if (state == OptionState.correct) ...[
                  const SizedBox(width: 8),
                  const Icon(Icons.check_circle_rounded,
                      color: Color(0xFF22C55E), size: 20),
                ],
                if (state == OptionState.incorrect) ...[
                  const SizedBox(width: 8),
                  const Icon(Icons.cancel_rounded,
                      color: Color(0xFFEF4444), size: 20),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }

  _OptionColors _colors() {
    switch (state) {
      case OptionState.correct:
        return const _OptionColors(
          bg: Color(0xFF0F2A1E),
          border: Color(0xFF22C55E),
          badgeBg: Color(0xFF22C55E),
          badgeText: Colors.white,
          text: Color(0xFFDCFCE7),
        );
      case OptionState.incorrect:
        return const _OptionColors(
          bg: Color(0xFF2A0F0F),
          border: Color(0xFFEF4444),
          badgeBg: Color(0xFFEF4444),
          badgeText: Colors.white,
          text: Color(0xFFFEE2E2),
        );
      case OptionState.staged:
        return const _OptionColors(
          bg: Color(0xFF1E243A),
          border: Color(0xFF6366F1),
          badgeBg: Color(0xFF6366F1),
          badgeText: Colors.white,
          text: Colors.white,
        );
      case OptionState.idle:
        return const _OptionColors(
          bg: Color(0xFF141824),
          border: Color(0xFF2D3347),
          badgeBg: Color(0xFF252B3B),
          badgeText: Color(0xFF9CA3AF),
          text: Color(0xFFD1D5DB),
        );
    }
  }
}

class _OptionColors {
  final Color bg, border, badgeBg, badgeText, text;
  const _OptionColors({
    required this.bg,
    required this.border,
    required this.badgeBg,
    required this.badgeText,
    required this.text,
  });
}
