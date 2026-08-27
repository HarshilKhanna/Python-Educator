import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/api_client.dart';
import '../services/auth_service.dart';
import 'activity_screen.dart';
import 'tutor_screen.dart';
import 'login_screen.dart';

// ---------------------------------------------------------------------------
// Topics definition
// ---------------------------------------------------------------------------

class _Topic {
  final String id;
  final String label;
  final IconData icon;
  final Color color;
  const _Topic(this.id, this.label, this.icon, this.color);
}

const _topics = [
  _Topic('loops', 'Loops', Icons.loop_rounded, Color(0xFF6366F1)),
  _Topic('conditionals', 'Conditionals', Icons.alt_route_rounded, Color(0xFF8B5CF6)),
  _Topic('lists', 'Lists', Icons.list_alt_rounded, Color(0xFF06B6D4)),
  _Topic('dictionaries', 'Dictionaries', Icons.data_object_rounded, Color(0xFF10B981)),
  _Topic('strings', 'Strings', Icons.text_fields_rounded, Color(0xFFF59E0B)),
  _Topic('files', 'Files & I/O', Icons.folder_open_rounded, Color(0xFFEF4444)),
  _Topic('basics-operators', 'Operators', Icons.calculate_rounded, Color(0xFF14B8A6)),
];

// ---------------------------------------------------------------------------
// Mastery provider
// ---------------------------------------------------------------------------

final masteryProvider = FutureProvider<Map<String, double>>((ref) async {
  try {
    final records = await apiClient.fetchMastery();
    return {
      for (final r in records)
        (r['topic_id'] as String): (r['mastery_level'] as num).toDouble()
    };
  } catch (_) {
    return {};
  }
});

// ---------------------------------------------------------------------------
// HomeScreen
// ---------------------------------------------------------------------------

class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final masteryAsync = ref.watch(masteryProvider);

    return Scaffold(
      backgroundColor: const Color(0xFF0A0E1A),
      body: SafeArea(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _Header(onLogout: () => _logout(context)),
            Expanded(
              child: masteryAsync.when(
                data: (mastery) => _TopicGrid(mastery: mastery),
                loading: () => const Center(
                  child: CircularProgressIndicator(
                    color: Color(0xFF6366F1),
                    strokeWidth: 2.5,
                  ),
                ),
                error: (e, _) => _TopicGrid(mastery: const {}),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _logout(BuildContext context) async {
    await authService.clearToken();
    if (context.mounted) {
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(builder: (_) => const LoginScreen()),
      );
    }
  }
}

// ---------------------------------------------------------------------------
// Header
// ---------------------------------------------------------------------------

class _Header extends StatelessWidget {
  final VoidCallback onLogout;
  const _Header({required this.onLogout});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(24, 20, 20, 0),
      child: Row(
        children: [
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Python Educator',
                style: TextStyle(
                  color: Colors.white.withOpacity(0.9),
                  fontSize: 22,
                  fontWeight: FontWeight.w700,
                  letterSpacing: -0.3,
                ),
              ),
              const SizedBox(height: 2),
              const Text(
                'Choose a topic to practice',
                style: TextStyle(
                  color: Color(0xFF6B7280),
                  fontSize: 13,
                ),
              ),
            ],
          ),
          const Spacer(),
          IconButton(
            icon: const Icon(Icons.logout_rounded,
                color: Color(0xFF6B7280), size: 20),
            onPressed: onLogout,
            tooltip: 'Logout',
          ),
        ],
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// Topic grid
// ---------------------------------------------------------------------------

class _TopicGrid extends StatelessWidget {
  final Map<String, double> mastery;
  const _TopicGrid({required this.mastery});

  @override
  Widget build(BuildContext context) {
    return GridView.builder(
      padding: const EdgeInsets.all(20),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        mainAxisSpacing: 14,
        crossAxisSpacing: 14,
        childAspectRatio: 1.05,
      ),
      itemCount: _topics.length,
      itemBuilder: (context, i) {
        final topic = _topics[i];
        final m = mastery[topic.id] ?? 0.0;
        return _TopicCard(topic: topic, mastery: m);
      },
    );
  }
}

// ---------------------------------------------------------------------------
// Topic card
// ---------------------------------------------------------------------------

class _TopicCard extends StatelessWidget {
  final _Topic topic;
  final double mastery;
  const _TopicCard({required this.topic, required this.mastery});

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        borderRadius: BorderRadius.circular(16),
        onTap: () => _showActions(context),
        child: Container(
          decoration: BoxDecoration(
            color: const Color(0xFF141824),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(
              color: topic.color.withOpacity(0.2),
              width: 1,
            ),
          ),
          padding: const EdgeInsets.all(18),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Icon badge
              Container(
                width: 44,
                height: 44,
                decoration: BoxDecoration(
                  color: topic.color.withOpacity(0.12),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: topic.color.withOpacity(0.25),
                  ),
                ),
                child: Icon(topic.icon, color: topic.color, size: 22),
              ),
              const Spacer(),
              Text(
                topic.label,
                style: const TextStyle(
                  color: Color(0xFFF9FAFB),
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 6),
              // Mastery bar
              ClipRRect(
                borderRadius: BorderRadius.circular(4),
                child: LinearProgressIndicator(
                  value: mastery,
                  backgroundColor: const Color(0xFF1F2937),
                  valueColor: AlwaysStoppedAnimation(topic.color),
                  minHeight: 4,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                'Mastery: ${(mastery * 100).toInt()}%',
                style: const TextStyle(
                  color: Color(0xFF6B7280),
                  fontSize: 11,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _showActions(BuildContext context) {
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
              // Handle
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
              Row(
                children: [
                  Icon(topic.icon, color: topic.color, size: 20),
                  const SizedBox(width: 10),
                  Text(
                    topic.label,
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 17,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 20),
              _ActionButton(
                icon: Icons.quiz_rounded,
                label: 'Practice Activities',
                subtitle: 'Work through exercises',
                color: topic.color,
                onTap: () {
                  Navigator.pop(context);
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (_) => ActivityScreen(topicId: topic.id),
                    ),
                  );
                },
              ),
              const SizedBox(height: 12),
              _ActionButton(
                icon: Icons.chat_bubble_outline_rounded,
                label: 'Ask the Tutor',
                subtitle: 'Get AI-powered explanations',
                color: const Color(0xFF10B981),
                onTap: () {
                  Navigator.pop(context);
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (_) => TutorScreen(topicId: topic.id, topicLabel: topic.label),
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

class _ActionButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final String subtitle;
  final Color color;
  final VoidCallback onTap;
  const _ActionButton({
    required this.icon,
    required this.label,
    required this.subtitle,
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
            color: color.withOpacity(0.08),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: color.withOpacity(0.2)),
          ),
          child: Row(
            children: [
              Container(
                width: 38,
                height: 38,
                decoration: BoxDecoration(
                  color: color.withOpacity(0.15),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Icon(icon, color: color, size: 20),
              ),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(label,
                        style: const TextStyle(
                            color: Colors.white,
                            fontSize: 14,
                            fontWeight: FontWeight.w600)),
                    Text(subtitle,
                        style: const TextStyle(
                            color: Color(0xFF6B7280), fontSize: 12)),
                  ],
                ),
              ),
              Icon(Icons.arrow_forward_ios_rounded,
                  color: color.withOpacity(0.6), size: 14),
            ],
          ),
        ),
      ),
    );
  }
}
