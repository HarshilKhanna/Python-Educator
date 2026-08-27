/// curriculum.dart — Client-side mirror of the Pedagogical Agent's curriculum DAG.
///
/// Mirrors `backend/agents/pedagogical.py::CURRICULUM_GRAPH` exactly.
/// Used to compute lock/unlock state for the home screen section tree without
/// needing an extra API round-trip.
///
/// If the curriculum changes server-side, update this file to match.

const double masteryThreshold = 0.7;

/// Ordered topic list — entry point for new students is index 0.
const List<String> curriculumOrder = [
  'basics-operators',
  'conditionals',
  'loops',
  'lists',
  'strings',
  'dictionaries',
  'files',
];

/// Prerequisite DAG: topic_id → list of prerequisite topic_ids.
const Map<String, List<String>> curriculumGraph = {
  'basics-operators': [],
  'conditionals': ['basics-operators'],
  'loops': ['conditionals'],
  'lists': ['loops'],
  'strings': ['lists'],
  'dictionaries': ['strings'],
  'files': ['dictionaries'],
};

/// Topic display metadata for the home screen.
class TopicMeta {
  final String id;
  final String label;
  final String emoji;

  const TopicMeta({required this.id, required this.label, required this.emoji});
}

const List<TopicMeta> topicMeta = [
  TopicMeta(id: 'basics-operators', label: 'Operators & Basics', emoji: '⚡'),
  TopicMeta(id: 'conditionals',     label: 'Conditionals',       emoji: '🔀'),
  TopicMeta(id: 'loops',            label: 'Loops',              emoji: '🔄'),
  TopicMeta(id: 'lists',            label: 'Lists',              emoji: '📋'),
  TopicMeta(id: 'strings',          label: 'Strings',            emoji: '🔤'),
  TopicMeta(id: 'dictionaries',     label: 'Dictionaries',       emoji: '📖'),
  TopicMeta(id: 'files',            label: 'Files & I/O',        emoji: '📁'),
];

/// Returns true if all prerequisites for [topicId] are at or above [masteryThreshold].
bool isTopicUnlocked(String topicId, Map<String, double> masteryMap) {
  final prereqs = curriculumGraph[topicId] ?? [];
  for (final prereq in prereqs) {
    if ((masteryMap[prereq] ?? 0.0) < masteryThreshold) return false;
  }
  return true;
}

/// Returns the names of the blocking prerequisites (those below threshold).
List<String> blockingPrereqs(String topicId, Map<String, double> masteryMap) {
  final prereqs = curriculumGraph[topicId] ?? [];
  return prereqs.where((p) => (masteryMap[p] ?? 0.0) < masteryThreshold).toList();
}

/// Returns the label for a topic ID, falling back to the raw ID.
String topicLabel(String topicId) {
  return topicMeta.firstWhere(
    (t) => t.id == topicId,
    orElse: () => TopicMeta(id: topicId, label: topicId, emoji: '📚'),
  ).label;
}
