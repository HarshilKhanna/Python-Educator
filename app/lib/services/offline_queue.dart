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
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';

import 'api_client.dart';
import 'auth_service.dart';

/// Callback invoked when the queue detects an expired token during sync.
/// The calling widget should show a re-login prompt.
typedef TokenExpiredCallback = void Function();

class OfflineQueue {
  static const String _dbName = 'offline_queue.db';
  static const String _tableName = 'failed_submissions';
  Database? _db;

  Future<Database?> get database async {
    if (kIsWeb) return null; // sqflite is not supported on web
    if (_db != null) return _db;
    _db = await _initDB();
    return _db;
  }

  Future<Database> _initDB() async {
    final dbPath = await getDatabasesPath();
    final path = join(dbPath, _dbName);

    return await openDatabase(
      path,
      version: 1,
      onCreate: (db, version) async {
        await db.execute('''
          CREATE TABLE $_tableName (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            activityId TEXT NOT NULL,
            submittedAnswer TEXT NOT NULL,
            authToken TEXT,
            enqueuedAt TEXT NOT NULL
          )
        ''');
      },
    );
  }

  /// Adds a failed submission to the local SQLite queue, capturing the current token.
  Future<void> enqueueAnswer({
    required String activityId,
    required String submittedAnswer,
    String? authToken,
  }) async {
    final db = await database;
    if (db == null) return;
    await db.insert(_tableName, {
      'activityId': activityId,
      'submittedAnswer': submittedAnswer,
      'authToken': authToken,
      'enqueuedAt': DateTime.now().toIso8601String(),
    });
  }

  /// Attempts to sync all queued items to the backend.
  /// Returns the number of items successfully synced.
  Future<int> syncQueue({
    TokenExpiredCallback? onTokenExpired,
  }) async {
    final db = await database;
    if (db == null) return 0;
    final items = await db.query(_tableName, orderBy: 'enqueuedAt ASC');

    if (items.isEmpty) return 0;

    int syncedCount = 0;

    for (final item in items) {
      final token = item['authToken'] as String?;
      final id = item['id'] as int;

      if (token == null || authService.isTokenExpired(token)) {
        onTokenExpired?.call();
        break;
      }

      try {
        await _submitWithToken(
          token: token,
          activityId: item['activityId'] as String,
          submittedAnswer: item['submittedAnswer'] as String,
        );
        // On success, remove from DB
        await db.delete(_tableName, where: 'id = ?', whereArgs: [id]);
        syncedCount++;
      } on AuthException {
        onTokenExpired?.call();
        break;
      } catch (_) {
        break;
      }
    }
    return syncedCount;
  }

  /// Returns the number of items currently waiting in the queue.
  Future<int> pendingCount() async {
    final db = await database;
    if (db == null) return 0;
    final count = Sqflite.firstIntValue(await db.rawQuery('SELECT COUNT(*) FROM $_tableName'));
    return count ?? 0;
  }

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
