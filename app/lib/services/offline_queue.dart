import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import 'api_client.dart';

class OfflineQueue {
  static const String _queueKey = 'offline_answer_queue';

  /// Adds a failed submission to the local queue.
  Future<void> enqueueAnswer({
    required String studentId,
    required String activityId,
    required String submittedAnswer,
  }) async {
    final prefs = await SharedPreferences.getInstance();
    final queue = prefs.getStringList(_queueKey) ?? [];
    
    final item = jsonEncode({
      'studentId': studentId,
      'activityId': activityId,
      'submittedAnswer': submittedAnswer,
    });
    
    queue.add(item);
    await prefs.setStringList(_queueKey, queue);
  }

  /// Attempts to sync all queued items to the backend.
  /// Returns the number of items successfully synced.
  Future<int> syncQueue() async {
    final prefs = await SharedPreferences.getInstance();
    final queue = prefs.getStringList(_queueKey) ?? [];
    
    if (queue.isEmpty) return 0;
    
    int syncedCount = 0;
    List<String> failedItems = [];
    
    for (final itemStr in queue) {
      try {
        final item = jsonDecode(itemStr);
        await apiClient.submitAnswer(
          studentId: item['studentId'],
          activityId: item['activityId'],
          submittedAnswer: item['submittedAnswer'],
        );
        syncedCount++;
      } catch (e) {
        // Stop syncing on first failure to maintain order, or just keep failed ones.
        // Let's keep failed ones and break to avoid spamming a down server.
        failedItems.add(itemStr);
        break;
      }
    }
    
    // Add remaining unsynced items back
    if (syncedCount < queue.length) {
      failedItems.addAll(queue.skip(syncedCount + failedItems.length));
    }
    
    await prefs.setStringList(_queueKey, failedItems);
    return syncedCount;
  }
}

final offlineQueue = OfflineQueue();
