import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../models/activity.dart';
import '../providers/activity_session_provider.dart';
import 'difficulty_badge.dart';

class ReorderLinesWidget extends ConsumerStatefulWidget {
  final Activity activity;

  const ReorderLinesWidget({super.key, required this.activity});

  @override
  ConsumerState<ReorderLinesWidget> createState() => _ReorderLinesWidgetState();
}

class _ReorderLinesWidgetState extends ConsumerState<ReorderLinesWidget> {
  late List<String> _lines;

  @override
  void initState() {
    super.initState();
    _lines = List<String>.from(widget.activity.options ?? []);
  }

  void _onReorder(int oldIndex, int newIndex) {
    setState(() {
      if (newIndex > oldIndex) {
        newIndex -= 1;
      }
      final item = _lines.removeAt(oldIndex);
      _lines.insert(newIndex, item);
    });
  }

  void _submit() {
    final answer = _lines.join('|');
    ref.read(activitySessionProvider.notifier).selectAnswer(answer);
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
        const SizedBox(height: 24),
        
        // Reorderable list
        Container(
          decoration: BoxDecoration(
            color: const Color(0xFF0D1117),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: Colors.white.withValues(alpha: 0.08),
              width: 1,
            ),
          ),
          clipBehavior: Clip.antiAlias,
          child: Theme(
            data: Theme.of(context).copyWith(
              canvasColor: const Color(0xFF141824), // background for dragging item
            ),
            child: ReorderableListView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: _lines.length,
              onReorder: isAnswered ? (_, _) {} : _onReorder,
              buildDefaultDragHandles: !isAnswered,
              itemBuilder: (context, index) {
                final line = _lines[index];
                return Container(
                  key: ValueKey('${line}_$index'),
                  decoration: BoxDecoration(
                    color: const Color(0xFF0D1117),
                    border: Border(
                      bottom: BorderSide(
                        color: index == _lines.length - 1
                            ? Colors.transparent
                            : Colors.white.withValues(alpha: 0.08),
                      ),
                    ),
                  ),
                  child: ListTile(
                    contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
                    title: Text(
                      line,
                      style: const TextStyle(
                        fontFamily: 'monospace',
                        fontSize: 13.5,
                        height: 1.5,
                        color: Color(0xFFE6EDF3),
                      ),
                    ),
                    trailing: isAnswered
                        ? null
                        : const Icon(Icons.drag_indicator_rounded, color: Color(0xFF6E7681)),
                  ),
                );
              },
            ),
          ),
        ),
        const SizedBox(height: 24),
        
        // Submit button
        if (!isAnswered)
          SizedBox(
            width: double.infinity,
            child: FilledButton(
              onPressed: _submit,
              style: FilledButton.styleFrom(
                backgroundColor: const Color(0xFF6366F1),
                padding: const EdgeInsets.symmetric(vertical: 15),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
              child: const Text(
                'Check Answer',
                style: TextStyle(fontSize: 15, fontWeight: FontWeight.w600),
              ),
            ),
          ),
          
        const SizedBox(height: 24),
      ],
    );
  }
}
