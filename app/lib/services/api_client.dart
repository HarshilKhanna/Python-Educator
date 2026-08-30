import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/activity.dart';
import '../config.dart';
import 'auth_service.dart';

/// Recommendation from the Pedagogical Agent via GET /activities/next.
class NextActivityRecommendation {
  final String topicId;
  final String activityType;
  final String reason;
  final double confidence;

  const NextActivityRecommendation({
    required this.topicId,
    required this.activityType,
    required this.reason,
    required this.confidence,
  });

  factory NextActivityRecommendation.fromJson(Map<String, dynamic> json) {
    return NextActivityRecommendation(
      topicId:      json['topic_id']      as String,
      activityType: json['activity_type'] as String,
      reason:       json['reason']        as String,
      confidence:   (json['confidence'] as num).toDouble(),
    );
  }
}

class ApiClient {
  static String get baseUrl => backendBaseUrl;

  Future<Map<String, String>> _authHeaders() async {
    final token = await authService.getToken();
    if (token == null) throw AuthException('Not authenticated. Please log in.');
    return {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $token',
    };
  }

  // ── Activities ────────────────────────────────────────────────────────────

  Future<List<Activity>> fetchActivities(String topicId) async {
    final headers = await _authHeaders();
    final response = await http.get(
      Uri.parse('$baseUrl/activities?topic_id=$topicId'),
      headers: headers,
    );
    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.map((json) => Activity.fromJson(json)).toList();
    } else if (response.statusCode == 401) {
      throw AuthException('Session expired. Please log in again.');
    } else {
      throw Exception('Failed to load activities: ${response.statusCode}');
    }
  }



  // ── Answers ───────────────────────────────────────────────────────────────

  /// Submit an answer. [confidence] is the student's self-reported certainty (0–1).
  Future<Map<String, dynamic>> submitAnswer({
    required String activityId,
    required String submittedAnswer,
    double? confidence,
  }) async {
    final headers = await _authHeaders();
    final body = <String, dynamic>{
      'activity_id': activityId,
      'submitted_answer': submittedAnswer,
    };
    if (confidence != null) body['confidence'] = confidence;

    final response = await http.post(
      Uri.parse('$baseUrl/answer'),
      headers: headers,
      body: jsonEncode(body),
    );
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return data as Map<String, dynamic>;
    } else if (response.statusCode == 401) {
      throw AuthException('Session expired. Please log in again.');
    } else {
      throw Exception('Failed to submit answer: ${response.statusCode}');
    }
  }

  // ── Tutor ─────────────────────────────────────────────────────────────────

  /// Send a free-text message to the tutor agent.
  Future<Map<String, dynamic>> tutorChat({
    required String message,
    String? topicId,
  }) async {
    final headers = await _authHeaders();
    final body = <String, dynamic>{'message': message};
    if (topicId != null) {
      body['topic_id'] = topicId;
    }
    final response = await http.post(
      Uri.parse('$baseUrl/tutor/interact'),
      headers: headers,
      body: jsonEncode(body),
    );
    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else if (response.statusCode == 401) {
      throw AuthException('Session expired. Please log in again.');
    } else {
      throw Exception('Tutor error: ${response.statusCode}');
    }
  }

  /// Stream a free-text message to the tutor agent.
  Stream<Map<String, dynamic>> tutorChatStream({
    required String message,
    String? topicId,
  }) async* {
    final headers = await _authHeaders();
    final body = <String, dynamic>{'message': message};
    if (topicId != null) {
      body['topic_id'] = topicId;
    }
    
    final request = http.Request('POST', Uri.parse('$baseUrl/tutor/stream'));
    request.headers.addAll(headers);
    request.body = jsonEncode(body);
    
    final response = await http.Client().send(request);
    
    if (response.statusCode == 401) {
      throw AuthException('Session expired. Please log in again.');
    } else if (response.statusCode != 200) {
      throw Exception('Tutor stream error: ${response.statusCode}');
    }
    
    await for (final line in response.stream.transform(utf8.decoder).transform(const LineSplitter())) {
      if (line.startsWith('data: ')) {
        final dataStr = line.substring(6).trim();
        if (dataStr.isEmpty) continue;
        
        try {
          final data = jsonDecode(dataStr) as Map<String, dynamic>;
          yield data;
        } catch (e) {
          // Ignore malformed JSON in stream
        }
      }
    }
  }

  /// Submit thumbs up/down feedback for a tutor message.
  Future<void> submitTutorFeedback({
    required String topicId,
    required String messageId,
    required String rating, // 'up' or 'down'
  }) async {
    final headers = await _authHeaders();
    final response = await http.post(
      Uri.parse('$baseUrl/tutor/feedback'),
      headers: headers,
      body: jsonEncode({
        'topic_id': topicId,
        'message_id': messageId,
        'rating': rating,
      }),
    );
    if (response.statusCode == 200) {
      return;
    } else if (response.statusCode == 401) {
      throw AuthException('Session expired. Please log in again.');
    } else {
      throw Exception('Failed to submit feedback: ${response.statusCode}');
    }
  }

  // ── Mastery ───────────────────────────────────────────────────────────────

  /// Fetch per-topic mastery for the current student (decoded from JWT).
  Future<List<Map<String, dynamic>>> fetchMastery() async {
    final headers = await _authHeaders();
    final token = await authService.getToken();
    if (token == null) throw AuthException('Not authenticated.');
    final parts = token.split('.');
    if (parts.length < 2) throw Exception('Malformed token');
    final payload = utf8.decode(
      base64Url.decode(base64Url.normalize(parts[1])),
    );
    final sub =
        (jsonDecode(payload) as Map<String, dynamic>)['sub'] as String;
    final response = await http.get(
      Uri.parse('$baseUrl/students/$sub/mastery'),
      headers: headers,
    );
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body) as Map<String, dynamic>;
      return List<Map<String, dynamic>>.from(data['mastery'] ?? []);
    } else if (response.statusCode == 401) {
      throw AuthException('Session expired.');
    } else {
      return [];
    }
  }
}

/// Thrown when a request fails due to authentication/authorization issues.
class AuthException implements Exception {
  final String message;
  const AuthException(this.message);

  @override
  String toString() => 'AuthException: $message';
}

final apiClient = ApiClient();
