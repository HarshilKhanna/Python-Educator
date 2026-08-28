import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'package:python_educator_app/models/activity.dart';
import 'package:python_educator_app/providers/activity_session_provider.dart';
import 'package:python_educator_app/widgets/fill_blank_widget.dart';

void main() {
  setUpAll(() {
    SharedPreferences.setMockInitialValues({});
  });

  final testActivity = Activity(
    id: '124',
    topicId: 'test_topic',
    activityType: 'fill_blank',
    promptText: 'Fill in the blank:',
    codeSnippet: 'print(___)',
    correctAnswer: 'Hello',
    explanation: 'Basic string.',
    difficulty: 2,
    sourceSection: const SourceSection(file: 'test.md', heading: 'test'),
  );

  ProviderContainer createContainer() {
    final container = ProviderContainer();
    container
        .read(activitySessionProvider.notifier)
        .loadActivities([testActivity]);
    return container;
  }

  Widget wrap(ProviderContainer container) {
    return UncontrolledProviderScope(
      container: container,
      child: MaterialApp(
        home: Scaffold(
          body: FillBlankWidget(activity: testActivity),
        ),
      ),
    );
  }

  testWidgets('fill_blank - correct answer path', (tester) async {
    final container = createContainer();
    await tester.pumpWidget(wrap(container));

    // Type the correct answer
    await tester.enterText(find.byType(TextField), 'Hello');
    await tester.testTextInput.receiveAction(TextInputAction.done);
    await tester.pumpAndSettle();
    
    // Simulate confidence check-in submission
    container.read(activitySessionProvider.notifier).submitStagedAnswer(0.8);
    await tester.pumpAndSettle();
    
    await tester.pump(const Duration(milliseconds: 500));

    final state = container.read(activitySessionProvider);
    expect(state.isAnswered, isTrue);
    expect(state.isCorrect, isTrue);
    // expect(state.isOffline, isTrue); // Network call fails -> queued offline
    expect(state.streak, 1);

    // Verify TextField is disabled
    final textField = tester.widget<TextField>(find.byType(TextField));
    expect(textField.enabled, isFalse);
  });

  testWidgets('fill_blank - incorrect answer path', (tester) async {
    final container = createContainer();
    await tester.pumpWidget(wrap(container));

    // Type the incorrect answer
    await tester.enterText(find.byType(TextField), 'Wrong');
    await tester.testTextInput.receiveAction(TextInputAction.done);
    await tester.pumpAndSettle();
    
    // Simulate confidence check-in submission
    container.read(activitySessionProvider.notifier).submitStagedAnswer(0.8);
    await tester.pumpAndSettle();
    
    await tester.pump(const Duration(milliseconds: 500));

    final state = container.read(activitySessionProvider);
    expect(state.isAnswered, isTrue);
    expect(state.isCorrect, isFalse);
    // expect(state.isOffline, isTrue);
    expect(state.streak, 0);
  });
}
