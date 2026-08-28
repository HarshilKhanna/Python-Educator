import 'dart:convert';

/// Back-reference into the handbook file where this activity was grounded.
class SourceSection {
  final String file;
  final String heading;

  const SourceSection({required this.file, required this.heading});

  factory SourceSection.fromJson(Map<String, dynamic> json) {
    return SourceSection(
      file: json['file'] as String,
      heading: json['heading'] as String,
    );
  }
}

/// Maps 1-to-1 with /docs/schema/activity.schema.json.
class Activity {
  final String id;
  final String topicId;
  final String activityType;
  final String promptText;
  final String? codeSnippet;
  final List<String>? options;
  final String correctAnswer;
  final String explanation;
  final int difficulty;
  final SourceSection sourceSection;

  const Activity({
    required this.id,
    required this.topicId,
    required this.activityType,
    required this.promptText,
    this.codeSnippet,
    this.options,
    required this.correctAnswer,
    required this.explanation,
    required this.difficulty,
    required this.sourceSection,
  });

  factory Activity.fromJson(Map<String, dynamic> json) {
    return Activity(
      id: json['id'] as String,
      topicId: json['topic_id'] as String,
      activityType: json['activity_type'] as String,
      promptText: json['prompt_text'] as String,
      codeSnippet: json['code_snippet'] as String?,
      options: () {
        final opts = (json['options'] as List<dynamic>?)
            ?.map((e) => e as String)
            .toList();
        opts?.shuffle();
        return opts;
      }(),
      correctAnswer: json['correct_answer'] as String,
      explanation: json['explanation'] as String,
      difficulty: json['difficulty'] as int,
      sourceSection: SourceSection.fromJson(
        json['source_section'] as Map<String, dynamic>,
      ),
    );
  }

  /// Parses the top-level { "activities": [...] } envelope.
  static List<Activity> listFromJson(String jsonString) {
    final data = jsonDecode(jsonString) as Map<String, dynamic>;
    final list = data['activities'] as List<dynamic>;
    return list
        .map((e) => Activity.fromJson(e as Map<String, dynamic>))
        .toList();
  }
}
