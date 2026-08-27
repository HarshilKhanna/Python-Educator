import 'package:flutter/material.dart';
import '../models/curriculum.dart';
import 'activity_screen.dart';
import 'tutor_screen.dart';

class SectionDetailScreen extends StatelessWidget {
  final TopicNode meta;
  final double masteryLevel;

  const SectionDetailScreen({
    super.key,
    required this.meta,
    required this.masteryLevel,
  });

  @override
  Widget build(BuildContext context) {
    final unlocked = true; // By definition, since we reached this screen
    final accentColor = const Color(0xFF6366F1);

    return Scaffold(
      backgroundColor: const Color(0xFF0A0E1A),
      appBar: AppBar(
        backgroundColor: const Color(0xFF141824),
        foregroundColor: Colors.white,
        elevation: 0,
        title: Text(meta.label, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600)),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_rounded, size: 18),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header
              Row(
                children: [
                  Text(meta.emoji, style: const TextStyle(fontSize: 48)),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          meta.label,
                          style: const TextStyle(
                              color: Colors.white,
                              fontSize: 24,
                              fontWeight: FontWeight.bold),
                        ),
                        const SizedBox(height: 4),
                        const Text(
                          'Estimated time: ~10 mins',
                          style: TextStyle(color: Color(0xFF9CA3AF), fontSize: 14),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 32),

              // Mastery
              const Text(
                'Your Mastery',
                style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.w600),
              ),
              const SizedBox(height: 12),
              ClipRRect(
                borderRadius: BorderRadius.circular(6),
                child: LinearProgressIndicator(
                  value: masteryLevel.clamp(0.0, 1.0),
                  backgroundColor: const Color(0xFF1F2937),
                  valueColor: AlwaysStoppedAnimation(accentColor),
                  minHeight: 8,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                '${(masteryLevel * 100).toInt()}% mastered',
                style: const TextStyle(color: Color(0xFF9CA3AF), fontSize: 14),
              ),
              
              const SizedBox(height: 48),

              // Actions
              const Text(
                'Up Next',
                style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.w600),
              ),
              const SizedBox(height: 16),
              
              _ActionCard(
                icon: Icons.quiz_rounded,
                title: 'Practice Activities',
                subtitle: 'Work through adaptive exercises',
                color: const Color(0xFF6366F1),
                onTap: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (_) => ActivityScreen(topicId: meta.id),
                    ),
                  );
                },
              ),
              const SizedBox(height: 16),
              _ActionCard(
                icon: Icons.chat_bubble_outline_rounded,
                title: 'Ask the Tutor',
                subtitle: 'Get AI-powered explanations',
                color: const Color(0xFF10B981),
                onTap: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (_) => TutorScreen(
                        topicId: meta.id,
                        topicLabel: meta.label,
                      ),
                    ),
                  );
                },
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _ActionCard extends StatelessWidget {
  final IconData icon;
  final String title;
  final String subtitle;
  final Color color;
  final VoidCallback onTap;

  const _ActionCard({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.color,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(16),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: const Color(0xFF141824),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: const Color(0xFF2D3347)),
        ),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: color.withValues(alpha: 0.15),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(icon, color: color, size: 24),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: const TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.w600),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    subtitle,
                    style: const TextStyle(color: Color(0xFF9CA3AF), fontSize: 13),
                  ),
                ],
              ),
            ),
            const Icon(Icons.arrow_forward_ios_rounded, color: Color(0xFF4B5563), size: 16),
          ],
        ),
      ),
    );
  }
}
