import 'package:flutter/material.dart';

/// Shared difficulty badge used by all activity-type widgets.
class DifficultyBadge extends StatelessWidget {
  final int difficulty;

  const DifficultyBadge({super.key, required this.difficulty});

  @override
  Widget build(BuildContext context) {
    const labels = {1: 'Introductory', 2: 'Practise', 3: 'Stretch'};
    const colors = {
      1: Color(0xFF3B82F6),
      2: Color(0xFFF59E0B),
      3: Color(0xFFEF4444),
    };
    final c = colors[difficulty] ?? Colors.grey;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: c.withValues(alpha: 0.15),
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: c.withValues(alpha: 0.4)),
      ),
      child: Text(
        labels[difficulty] ?? 'Level $difficulty',
        style: TextStyle(
          color: c,
          fontSize: 11,
          fontWeight: FontWeight.w600,
          letterSpacing: 0.6,
        ),
      ),
    );
  }
}
