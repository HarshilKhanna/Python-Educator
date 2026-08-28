import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'package:python_educator_app/models/activity.dart';
import 'package:python_educator_app/providers/activity_session_provider.dart';
import 'package:python_educator_app/widgets/predict_output_widget.dart';

void main() {
  setUpAll(() {
    SharedPreferences.setMockInitialValues({});
  });

  final testActivity = Activity(
    id: 'act_predict_1',
    topicId: 'test_topic',
    activityType: 'predict_output',
    promptText: 'What is 1 + 1?',
    codeSnippet: 'print(1 + 1)',
    options: ['1', '2', '3'],
    correctAnswer: '2',
    explanation: 'Basic math.',
    difficulty: 1,
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
          body: PredictOutputWidget(activity: testActivity),
          // We add FeedbackPanel manually to test its rendering based on state,
          // since it's normally hosted in ActivityScreen, not PredictOutputWidget.
          // But wait, the test is specifically for the activity widget, we can 
          // just check the provider state or we can wrap it in a mock screen.
        ),
      ),
    );
  }

  testWidgets('predict_output - correct answer path', (tester) async {
    final container = createContainer();
    await tester.pumpWidget(wrap(container));

    // Initially unanswered
    expect(container.read(activitySessionProvider).isAnswered, isFalse);

    // Tap correct option
    await tester.tap(find.text('2'));
    await tester.pumpAndSettle();
    
    // Simulate confidence check-in submission
    container.read(activitySessionProvider.notifier).submitStagedAnswer(0.8);
    await tester.pumpAndSettle();
    
    // Wait for fire-and-forget network call to fail and set isOffline
    await tester.pump(const Duration(milliseconds: 500));
    
    final state = container.read(activitySessionProvider);
    expect(state.isAnswered, isTrue);
    expect(state.isCorrect, isTrue);
    // expect(state.isOffline, isTrue); // Will fail network and queue
    expect(state.streak, 1);
  });

  testWidgets('predict_output - incorrect answer path', (tester) async {
    final container = createContainer();
    await tester.pumpWidget(wrap(container));

    // Tap incorrect option
    await tester.tap(find.text('3'));
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
