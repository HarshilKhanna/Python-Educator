import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/api_client.dart';

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
