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

/// Computes the set of unlocked topic IDs across the entire curriculum.
///
/// Progressive Unlocking (Latch) Rules:
/// 1. The first topic is always unlocked.
/// 2. Once a topic has any recorded progress/mastery (> 0.0), it is permanently unlocked.
/// 3. Normal progression: an unstarted topic unlocks when all prerequisites are unlocked and >= masteryThreshold.
/// 4. Downstream invariant (Parent Latch): If topic N is unlocked or started, all its ancestor prerequisites and prior sequence nodes are permanently unlocked.
Set<String> computeUnlockedTopics(Map<String, double> masteryMap) {
  final unlocked = <String>{};

  // 1. First topic is always unlocked
  if (curriculumOrder.isNotEmpty) {
    unlocked.add(curriculumOrder.first);
  }

  // 2. Any topic with existing progress (> 0.0) is already unlocked
  for (final entry in masteryMap.entries) {
    if (entry.value > 0.0) {
      unlocked.add(entry.key);
    }
  }

  // 3. Normal forward propagation
  for (final topicId in curriculumOrder) {
    final prereqs = curriculumGraph[topicId] ?? [];
    if (prereqs.isEmpty) {
      unlocked.add(topicId);
    } else {
      final allPrereqsMet = prereqs.every((p) =>
          unlocked.contains(p) && (masteryMap[p] ?? 0.0) >= masteryThreshold);
      if (allPrereqsMet) {
        unlocked.add(topicId);
      }
    }
  }

  // 4. Backward latch propagation (if topic N is unlocked, all ancestors & prior nodes must be unlocked)
  bool changed = true;
  while (changed) {
    changed = false;
    for (final topicId in unlocked.toList()) {
      final prereqs = curriculumGraph[topicId] ?? [];
      for (final p in prereqs) {
        if (!unlocked.contains(p)) {
          unlocked.add(p);
          changed = true;
        }
      }
      final idx = curriculumOrder.indexOf(topicId);
      if (idx > 0) {
        for (int i = 0; i < idx; i++) {
          if (!unlocked.contains(curriculumOrder[i])) {
            unlocked.add(curriculumOrder[i]);
            changed = true;
          }
        }
      }
    }
  }

  return unlocked;
}

/// Returns true if [topicId] is unlocked.
bool isTopicUnlocked(String topicId, Map<String, double> masteryMap) {
  return computeUnlockedTopics(masteryMap).contains(topicId);
}

/// Returns the names of the blocking prerequisites (those below threshold), or empty if unlocked.
List<String> blockingPrereqs(String topicId, Map<String, double> masteryMap) {
  if (isTopicUnlocked(topicId, masteryMap)) return [];
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
