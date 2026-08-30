import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/curriculum.dart' as curr;
import '../providers/settings_provider.dart';
import '../providers/mastery_provider.dart';
import '../services/api_client.dart';
import '../services/auth_service.dart';
import 'section_detail_screen.dart';
import 'login_screen.dart';

// ── HomeScreen ──────────────────────────────────────────────────────────────

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
            _Header(
              onLogout:   () => _logout(context),
              onSettings: () => _showSettings(context),
            ),
            Expanded(
              child: masteryAsync.when(
                data: (mastery) => _CurriculumPath(
                  mastery: mastery,
                  onReturn: () {
                    ref.invalidate(masteryProvider);
                  },
                ),
                loading: () => const Center(
                  child: CircularProgressIndicator(
                    color: Color(0xFF6366F1),
                    strokeWidth: 2.5,
                  ),
                ),
                error: (e, _) => _ErrorRetry(
                  message: 'Could not load your progress.',
                  onRetry: () => ref.invalidate(masteryProvider),
                ),
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

  void _showSettings(BuildContext context) {
    showModalBottomSheet(
      context: context,
      backgroundColor: const Color(0xFF141824),
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (_) => const _SettingsSheet(),
    );
  }
}

// ── Header ──────────────────────────────────────────────────────────────────

class _Header extends StatelessWidget {
  final VoidCallback onLogout;
  final VoidCallback onSettings;
  const _Header({required this.onLogout, required this.onSettings});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(24, 20, 16, 0),
      child: Row(
        children: [
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Python Educator',
                style: TextStyle(
                  color: Colors.white.withValues(alpha: 0.9),
                  fontSize: 22,
                  fontWeight: FontWeight.w700,
                  letterSpacing: -0.3,
                ),
              ),
              const SizedBox(height: 2),
              const Text(
                'Your learning path',
                style: TextStyle(color: Color(0xFF6B7280), fontSize: 13),
              ),
            ],
          ),
          const Spacer(),
          IconButton(
            icon: const Icon(Icons.settings_outlined,
                color: Color(0xFF6B7280), size: 20),
            onPressed: onSettings,
            tooltip: 'Settings',
          ),
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

// ── Curriculum path ─────────────────────────────────────────────────────────

class _CurriculumPath extends StatelessWidget {
  final Map<String, double> mastery;
  final VoidCallback onReturn;
  const _CurriculumPath({required this.mastery, required this.onReturn});

  @override
  Widget build(BuildContext context) {
    return RefreshIndicator(
      onRefresh: () async => onReturn(),
      color: const Color(0xFF6366F1),
      backgroundColor: const Color(0xFF141824),
      child: ListView.builder(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.fromLTRB(20, 24, 20, 32),
        itemCount: curr.curriculumOrder.length,
        itemBuilder: (context, i) {
          final topicId = curr.curriculumOrder[i];
          final meta    = curr.topicMeta.firstWhere(
            (t) => t.id == topicId,
            orElse: () => curr.TopicMeta(id: topicId, label: topicId, emoji: '📚'),
          );
          final masteryLevel = mastery[topicId] ?? 0.0;
          final unlocked     = curr.isTopicUnlocked(topicId, mastery);
          final blocking     = curr.blockingPrereqs(topicId, mastery);

          return _TopicNode(
            meta:         meta,
            masteryLevel: masteryLevel,
            unlocked:     unlocked,
            blockingPrereqs: blocking,
            isFirst:      i == 0,
            isLast:       i == curr.curriculumOrder.length - 1,
            onReturn:     onReturn,
          );
        },
      ),
    );
  }
}

// ── Topic node ──────────────────────────────────────────────────────────────

/// A node on the curriculum path — unlocked topics glow; locked ones show a padlock.
class _TopicNode extends StatelessWidget {
  final curr.TopicMeta meta;
  final double masteryLevel;
  final bool unlocked;
  final List<String> blockingPrereqs;
  final bool isFirst;
  final bool isLast;
  final VoidCallback onReturn;

  const _TopicNode({
    required this.meta,
    required this.masteryLevel,
    required this.unlocked,
    required this.blockingPrereqs,
    required this.isFirst,
    required this.isLast,
    required this.onReturn,
  });

  Color get _accentColor {
    if (masteryLevel >= curr.masteryThreshold) return const Color(0xFF10B981);
    if (unlocked) return const Color(0xFF6366F1);
    return const Color(0xFF4B5563);
  }

  @override
  Widget build(BuildContext context) {
    return IntrinsicHeight(
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // ── Vertical connector line ─────────────────────────────────────
          SizedBox(
            width: 48,
            child: Column(
              children: [
                if (!isFirst)
                  Expanded(
                    child: Center(
                      child: Container(
                        width: 2,
                        color: unlocked
                            ? _accentColor.withValues(alpha: 0.4)
                            : const Color(0xFF1F2937),
                      ),
                    ),
                  ),
                // Node circle
                Container(
                  width: 48,
                  height: 48,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: unlocked
                        ? _accentColor.withValues(alpha: 0.12)
                        : const Color(0xFF1A1F2E),
                    border: Border.all(
                      color: _accentColor.withValues(alpha: unlocked ? 0.6 : 0.2),
                      width: unlocked ? 2 : 1,
                    ),
                    boxShadow: unlocked && masteryLevel < curr.masteryThreshold
                        ? [
                            BoxShadow(
                              color: _accentColor.withValues(alpha: 0.25),
                              blurRadius: 12,
                              spreadRadius: 1,
                            ),
                          ]
                        : null,
                  ),
                  child: Center(
                    child: unlocked
                        ? Text(meta.emoji, style: const TextStyle(fontSize: 20))
                        : const Icon(Icons.lock_rounded,
                            color: Color(0xFF4B5563), size: 18),
                  ),
                ),
                if (!isLast)
                  Expanded(
                    child: Center(
                      child: Container(
                        width: 2,
                        color: const Color(0xFF1F2937),
                      ),
                    ),
                  ),
              ],
            ),
          ),
          const SizedBox(width: 16),

          // ── Card ────────────────────────────────────────────────────────
          Expanded(
            child: Padding(
              padding: const EdgeInsets.symmetric(vertical: 8),
              child: _TopicCard(
                meta:            meta,
                masteryLevel:    masteryLevel,
                unlocked:        unlocked,
                blockingPrereqs: blockingPrereqs,
                accentColor:     _accentColor,
                onReturn:        onReturn,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

// ── Topic card ──────────────────────────────────────────────────────────────

class _TopicCard extends StatelessWidget {
  final curr.TopicMeta meta;
  final double masteryLevel;
  final bool unlocked;
  final List<String> blockingPrereqs;
  final Color accentColor;
  final VoidCallback onReturn;

  const _TopicCard({
    required this.meta,
    required this.masteryLevel,
    required this.unlocked,
    required this.blockingPrereqs,
    required this.accentColor,
    required this.onReturn,
  });

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        borderRadius: BorderRadius.circular(16),
        onTap: unlocked
            ? () async {
                await Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (_) => SectionDetailScreen(
                      meta: meta,
                      masteryLevel: masteryLevel,
                    ),
                  ),
                );
                onReturn();
              }
            : () => _showLockedDialog(context),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 300),
          decoration: BoxDecoration(
            color: const Color(0xFF141824),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(
              color: accentColor.withValues(alpha: unlocked ? 0.3 : 0.1),
              width: 1,
            ),
          ),
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Expanded(
                    child: Text(
                      meta.label,
                      style: TextStyle(
                        color: unlocked
                            ? const Color(0xFFF9FAFB)
                            : const Color(0xFF4B5563),
                        fontSize: 15,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                  if (unlocked && masteryLevel >= curr.masteryThreshold)
                    const Icon(Icons.verified_rounded,
                        color: Color(0xFF10B981), size: 16),
                ],
              ),
              const SizedBox(height: 10),

              // Mastery bar (reflects actual mastery, not completion)
              ClipRRect(
                borderRadius: BorderRadius.circular(4),
                child: LinearProgressIndicator(
                  value: masteryLevel.clamp(0.0, 1.0),
                  backgroundColor: const Color(0xFF1F2937),
                  valueColor: AlwaysStoppedAnimation(
                    unlocked ? accentColor : const Color(0xFF374151),
                  ),
                  minHeight: 4,
                ),
              ),
              const SizedBox(height: 6),

              Row(
                children: [
                  Text(
                    unlocked
                        ? 'Mastery: ${(masteryLevel * 100).toInt()}%'
                        : 'Locked',
                    style: TextStyle(
                      color: unlocked
                          ? const Color(0xFF6B7280)
                          : const Color(0xFF374151),
                      fontSize: 11,
                    ),
                  ),
                  if (!unlocked && blockingPrereqs.isNotEmpty) ...[
                    const SizedBox(width: 6),
                    Expanded(
                      child: Text(
                        '· Complete ${blockingPrereqs.map(curr.topicLabel).join(', ')} first',
                        style: const TextStyle(
                          color: Color(0xFF374151),
                          fontSize: 11,
                        ),
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                  ],
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _showLockedDialog(BuildContext context) {
    final prereqNames = blockingPrereqs.map(curr.topicLabel).join(', ');
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        backgroundColor: const Color(0xFF141824),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: Row(
          children: [
            const Icon(Icons.lock_rounded, color: Color(0xFF6366F1), size: 20),
            const SizedBox(width: 8),
            Text(meta.label,
                style: const TextStyle(color: Colors.white, fontSize: 16)),
          ],
        ),
        content: Text(
          prereqNames.isEmpty
              ? 'Complete earlier topics to unlock this one.'
              : 'You need to master $prereqNames (≥${(curr.masteryThreshold * 100).toInt()}%) to unlock ${meta.label}.',
          style: const TextStyle(color: Color(0xFF9CA3AF), fontSize: 13, height: 1.5),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Got it', style: TextStyle(color: Color(0xFF6366F1))),
          ),
        ],
      ),
    );
  }
}

// ── Error retry ─────────────────────────────────────────────────────────────

class _ErrorRetry extends StatelessWidget {
  final String message;
  final VoidCallback onRetry;
  const _ErrorRetry({required this.message, required this.onRetry});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.wifi_off_rounded, color: Color(0xFF4B5563), size: 48),
            const SizedBox(height: 16),
            Text(
              message,
              textAlign: TextAlign.center,
              style: const TextStyle(color: Color(0xFF6B7280), fontSize: 15),
            ),
            const SizedBox(height: 24),
            OutlinedButton.icon(
              onPressed: onRetry,
              icon: const Icon(Icons.refresh_rounded, size: 18),
              label: const Text('Try again'),
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
    );
  }
}

// ── Action button (bottom-sheet) ─────────────────────────────────────────────

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
            color: color.withValues(alpha: 0.08),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: color.withValues(alpha: 0.2)),
          ),
          child: Row(
            children: [
              Container(
                width: 38,
                height: 38,
                decoration: BoxDecoration(
                  color: color.withValues(alpha: 0.15),
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
                        style:
                            const TextStyle(color: Color(0xFF6B7280), fontSize: 12)),
                  ],
                ),
              ),
              Icon(Icons.arrow_forward_ios_rounded,
                  color: color.withValues(alpha: 0.6), size: 14),
            ],
          ),
        ),
      ),
    );
  }
}

// ── Settings bottom-sheet ────────────────────────────────────────────────────

class _SettingsSheet extends ConsumerWidget {
  const _SettingsSheet();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final settings = ref.watch(settingsProvider);
    final notifier = ref.read(settingsProvider.notifier);

    return SafeArea(
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
            const Text(
              'Accessibility',
              style: TextStyle(
                color: Colors.white,
                fontSize: 17,
                fontWeight: FontWeight.w700,
              ),
            ),
            const SizedBox(height: 20),

            // ── Text size ───────────────────────────────────────────────
            const Text('Text Size',
                style: TextStyle(color: Color(0xFF9CA3AF), fontSize: 13)),
            const SizedBox(height: 10),
            Row(
              children: TextScale.values.map((scale) {
                final selected = settings.textScale == scale;
                return Expanded(
                  child: Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 4),
                    child: GestureDetector(
                      onTap: () => notifier.setTextScale(scale),
                      child: AnimatedContainer(
                        duration: const Duration(milliseconds: 200),
                        padding: const EdgeInsets.symmetric(vertical: 10),
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
                        child: Text(
                          scale.label,
                          textAlign: TextAlign.center,
                          style: TextStyle(
                            color: selected
                                ? const Color(0xFF6366F1)
                                : const Color(0xFF6B7280),
                            fontSize: 13,
                            fontWeight: selected
                                ? FontWeight.w600
                                : FontWeight.w400,
                          ),
                        ),
                      ),
                    ),
                  ),
                );
              }).toList(),
            ),
            const SizedBox(height: 20),

            // ── High contrast ────────────────────────────────────────────
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'High Contrast',
                  style: TextStyle(color: Color(0xFF9CA3AF), fontSize: 13),
                ),
                Switch(
                  value: settings.highContrast,
                  onChanged: notifier.setHighContrast,
                  activeColor: const Color(0xFF6366F1),
                ),
              ],
            ),

            // ── Reduced motion ───────────────────────────────────────────
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'Reduced Motion',
                  style: TextStyle(color: Color(0xFF9CA3AF), fontSize: 13),
                ),
                Switch(
                  value: settings.reducedMotion,
                  onChanged: notifier.setReducedMotion,
                  activeColor: const Color(0xFF6366F1),
                ),
              ],
            ),

            // ── Dyslexia font ────────────────────────────────────────────
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'Dyslexia Font (OpenDyslexic)',
                  style: TextStyle(color: Color(0xFF9CA3AF), fontSize: 13),
                ),
                Switch(
                  value: settings.dyslexiaFont,
                  onChanged: notifier.setDyslexiaFont,
                  activeColor: const Color(0xFF6366F1),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
