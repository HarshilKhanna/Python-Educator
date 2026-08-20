import 'package:flutter/material.dart';

import '../models/activity.dart';
import 'fill_blank_widget.dart';
import 'predict_output_widget.dart';
import 'reorder_lines_widget.dart';

/// Generic dispatch point for all activity types.
///
/// To add a new type (e.g. fill_blank):
///   1. Create FillBlankWidget similar to PredictOutputWidget.
///   2. Add a new case below.
///   3. No other files need to change.
class ActivityRunner extends StatelessWidget {
  final Activity activity;

  const ActivityRunner({super.key, required this.activity});

  @override
  Widget build(BuildContext context) {
    return switch (activity.activityType) {
      'predict_output' => PredictOutputWidget(activity: activity),
      'fill_blank'     => FillBlankWidget(activity: activity),
      'reorder_lines'  => ReorderLinesWidget(activity: activity),
      // Future types plug in here:
      // 'spot_bug'      => SpotBugWidget(activity: activity),
      _ => _UnsupportedActivity(type: activity.activityType),
    };
  }
}

class _UnsupportedActivity extends StatelessWidget {
  final String type;
  const _UnsupportedActivity({required this.type});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Icon(Icons.build_circle_outlined, color: Colors.amber, size: 40),
          const SizedBox(height: 12),
          Text(
            'Activity type "$type" is not yet implemented.',
            textAlign: TextAlign.center,
            style: const TextStyle(color: Colors.amber, fontSize: 14),
          ),
        ],
      ),
    );
  }
}
