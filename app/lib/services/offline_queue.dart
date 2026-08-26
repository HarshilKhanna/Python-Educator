/// offline_queue.dart — Offline answer submission queue with auth-aware sync.
///
/// Design decisions for Phase 15.2:
///
/// 1. Queued items store the auth TOKEN (not student_id). The backend derives
///    identity from the token, so the queue must carry it.
///
/// 2. The auth token is stored as part of the queue item in shared_preferences.
///    This is acceptable because: the answer payload (activity_id, answer) is
///    not a credential, and the token is already stored in flutter_secure_storage.
///    The queue item needs the token at sync time, which may be minutes/hours later.
///
/// 3. If the token is expired at sync time, the queue STOPS and calls
///    [onTokenExpired] — it does NOT silently drop items or submit without auth.
///    The user must re-authenticate; the queue item is preserved.
library;

import 'dart:convert';

import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

import 'api_client.dart';
import 'auth_service.dart';

/// Callback invoked when the queue detects an expired token during sync.
/// The calling widget should show a re-login prompt.
typedef TokenExpiredCallback = void Function();

class OfflineQueue {
  static const String _queueKey = 'offline_answer_queue';

  /// Adds a failed submission to the local queue, capturing the current token.
  ///
  /// If there is no token (user is somehow not logged in), the item is still
  /// queued but will fail at sync time with an AuthException — surfaced to the
  /// caller via [onTokenExpired].
  Future<void> enqueueAnswer({
    required String activityId,
    required String submittedAnswer,
    String? authToken,
  }) async {
    final prefs = await SharedPreferences.getInstance();
    final queue = prefs.getStringList(_queueKey) ?? [];

    final item = jsonEncode({
      'activityId': activityId,
      'submittedAnswer': submittedAnswer,
      // Token stored so we can re-submit with correct identity even if the
      // currently active user has changed (e.g., shared device).
      'authToken': authToken,
      'enqueuedAt': DateTime.now().toIso8601String(),
    });

    queue.add(item);
    await prefs.setStringList(_queueKey, queue);
  }

  /// Attempts to sync all queued items to the backend.
  ///
  /// Returns the number of items successfully synced.
  ///
  /// [onTokenExpired] is called (and sync is halted) if the token for the
  /// front-of-queue item is expired. The item is NOT dropped — the user must
  /// re-authenticate before the queue can drain.
  Future<int> syncQueue({
    TokenExpiredCallback? onTokenExpired,
  }) async {
    final prefs = await SharedPreferences.getInstance();
    final queue = prefs.getStringList(_queueKey) ?? [];

    if (queue.isEmpty) return 0;

    int syncedCount = 0;
    final List<String> failedItems = [];

    for (final itemStr in queue) {
      final item = jsonDecode(itemStr) as Map<String, dynamic>;
      final token = item['authToken'] as String?;

      // ── Token expiry check ────────────────────────────────────────────────
      if (token == null || authService.isTokenExpired(token)) {
        // Token is gone or expired — do NOT drop the item, do NOT submit.
        // Surface the re-login prompt and stop processing.
        onTokenExpired?.call();
        // Re-add all remaining items (including this one) to the queue.
        failedItems.add(itemStr);
        final remaining = queue.skip(syncedCount + failedItems.length);
        failedItems.addAll(remaining);
        break;
      }

      // ── Attempt submission ────────────────────────────────────────────────
      try {
        await _submitWithToken(
          token: token,
          activityId: item['activityId'] as String,
          submittedAnswer: item['submittedAnswer'] as String,
        );
        syncedCount++;
      } on AuthException {
        // 401 from the server — token was accepted client-side but rejected
        // server-side (e.g., revoked). Treat the same as expiry.
        onTokenExpired?.call();
        failedItems.add(itemStr);
        final remaining = queue.skip(syncedCount + failedItems.length);
        failedItems.addAll(remaining);
        break;
      } catch (_) {
        // Network error — keep the item, stop processing to avoid hammering.
        failedItems.add(itemStr);
        final remaining = queue.skip(syncedCount + failedItems.length);
        failedItems.addAll(remaining);
        break;
      }
    }

    await prefs.setStringList(_queueKey, failedItems);
    return syncedCount;
  }

  /// Returns the number of items currently waiting in the queue.
  Future<int> pendingCount() async {
    final prefs = await SharedPreferences.getInstance();
    return (prefs.getStringList(_queueKey) ?? []).length;
  }

  /// Submit a single queued item using its stored token (not the currently
  /// active session token). This allows older queued answers from this session
  /// to drain correctly even if the user has re-authenticated.
  Future<void> _submitWithToken({
    required String token,
    required String activityId,
    required String submittedAnswer,
  }) async {
    final response = await http.post(
      Uri.parse('${ApiClient.baseUrl}/answer'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      },
      body: jsonEncode({
        'activity_id': activityId,
        'submitted_answer': submittedAnswer,
      }),
    );

    if (response.statusCode == 401) {
      throw const AuthException('Token rejected by server.');
    }
    if (response.statusCode != 200) {
      throw Exception('Sync failed: ${response.statusCode}');
    }
  }
}

final offlineQueue = OfflineQueue();
