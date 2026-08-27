import 'dart:math' as math;
import 'package:flutter/material.dart';
import '../services/api_client.dart';
import '../services/chat_history_service.dart';

// ── Message model ──────────────────────────────────────────────────────────

/// Full representation of one turn in the tutor conversation.
class _Message {
  final String id;
  final String role; // 'user' | 'assistant'
  final String text;
  final bool isError;

  // Source attribution fields (populated from /tutor/interact response)
  final bool? grounded;
  final List<Map<String, dynamic>>? sourceChunks;

  // Pedagogical recommendation fields
  final bool pendingReview;
  final String? riskTier;
  final bool autoApplied;
  final String? nextTopicId;
  final String? nextActivityType;
  final String? agentReason;

  _Message({
    String? id,
    required this.role,
    required this.text,
    this.isError = false,
    this.grounded,
    this.sourceChunks,
    this.pendingReview = false,
    this.riskTier,
    this.autoApplied = false,
    this.nextTopicId,
    this.nextActivityType,
    this.agentReason,
  }) : id = id ?? '${DateTime.now().millisecondsSinceEpoch}_${math.Random().nextInt(10000)}';

  Map<String, dynamic> toJson() => {
        'id': id,
        'role': role,
        'text': text,
        'isError': isError,
        'grounded': grounded,
        'sourceChunks': sourceChunks,
        'pendingReview': pendingReview,
        'riskTier': riskTier,
        'autoApplied': autoApplied,
        'nextTopicId': nextTopicId,
        'nextActivityType': nextActivityType,
        'agentReason': agentReason,
      };

  factory _Message.fromJson(Map<String, dynamic> json) => _Message(
        id: json['id'] as String?,
        role: json['role'] as String,
        text: json['text'] as String,
        isError: json['isError'] as bool? ?? false,
        grounded: json['grounded'] as bool?,
        sourceChunks: (json['sourceChunks'] as List<dynamic>?)
            ?.map((e) => e as Map<String, dynamic>)
            .toList(),
        pendingReview: json['pendingReview'] as bool? ?? false,
        riskTier: json['riskTier'] as String?,
        autoApplied: json['autoApplied'] as bool? ?? false,
        nextTopicId: json['nextTopicId'] as String?,
        nextActivityType: json['nextActivityType'] as String?,
        agentReason: json['agentReason'] as String?,
      );

  /// Build from the full /tutor/interact response map.
  factory _Message.fromResponse(Map<String, dynamic> data) {
    final intent = data['intent'] as String? ?? 'question';

    if (intent == 'activity_request') {
      final nextTopic    = data['next_topic_id']      as String?;
      final nextActivity = data['next_activity_type'] as String?;
      final reason       = data['reason']             as String?;
      final pending      = data['pending_review']     as bool? ?? false;
      final riskTier     = data['risk_tier']          as String?;
      final autoApplied  = data['auto_applied']       as bool? ?? false;

      String text;
      if (pending) {
        text = "I've suggested your next step: **$nextActivity** on **$nextTopic**.\n\n"
               "${reason ?? ''}";
      } else if (autoApplied) {
        text = "Ready for your next challenge! I'm setting up a **$nextActivity** "
               "activity on **$nextTopic**.\n\n${reason ?? ''}";
      } else {
        text = "Next up: **$nextActivity** on **$nextTopic**.\n\n${reason ?? ''}";
      }

      return _Message(
        role: 'assistant',
        text: text,
        pendingReview:    pending,
        riskTier:         riskTier,
        autoApplied:      autoApplied,
        nextTopicId:      nextTopic,
        nextActivityType: nextActivity,
        agentReason:      reason,
      );
    }

    // Technical / question path
    final answer  = data['answer']   as String?;
    final grounded = data['grounded'] as bool?;
    final chunks  = (data['source_chunks'] as List<dynamic>?)
        ?.map((e) => e as Map<String, dynamic>)
        .toList();

    return _Message(
      role:         'assistant',
      text:         answer ?? 'No response from tutor.',
      grounded:     grounded,
      sourceChunks: chunks,
    );
  }
}

// ── Screen ─────────────────────────────────────────────────────────────────

class TutorScreen extends StatefulWidget {
  final String topicId;
  final String topicLabel;
  const TutorScreen({super.key, required this.topicId, required this.topicLabel});

  @override
  State<TutorScreen> createState() => _TutorScreenState();
}

class _TutorScreenState extends State<TutorScreen> {
  final _controller     = TextEditingController();
  final _scrollController = ScrollController();
  final List<_Message>  _messages = [];
  bool _loading = false;

  static const _indigo  = Color(0xFF6366F1);
  static const _bg      = Color(0xFF0A0E1A);
  static const _surface = Color(0xFF141824);

  @override
  void initState() {
    super.initState();
    _loadHistory();
  }

  Future<void> _loadHistory() async {
    final history = await chatHistoryService.loadHistory(widget.topicId);
    if (history.isNotEmpty) {
      if (mounted) {
        setState(() {
          _messages.addAll(history.map((m) => _Message.fromJson(m)));
        });
        _scrollToBottom();
      }
    } else {
      if (mounted) {
        setState(() {
          _messages.add(_Message(
            role: 'assistant',
            text: 'Hi! I\'m your Python tutor for **${widget.topicLabel}**. '
                  'Ask me anything — or tap **Next activity** and I\'ll suggest '
                  'what to practice next based on your progress.',
          ));
        });
      }
    }
  }

  Future<void> _saveHistory() async {
    await chatHistoryService.saveHistory(
      widget.topicId,
      _messages.map((m) => m.toJson()).toList(),
    );
  }

  Future<void> _clearHistory() async {
    await chatHistoryService.clearHistory(widget.topicId);
    if (mounted) {
      setState(() {
        _messages.clear();
        _messages.add(_Message(
          role: 'assistant',
          text: 'History cleared. Hi! I\'m your Python tutor for **${widget.topicLabel}**. '
                'Ask me anything.',
        ));
      });
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  Future<void> _send() async {
    final text = _controller.text.trim();
    if (text.isEmpty || _loading) return;

    setState(() {
      _messages.add(_Message(role: 'user', text: text));
      _loading = true;
    });
    _saveHistory();
    _controller.clear();
    _scrollToBottom();

    try {
      final response = await apiClient.tutorChat(
        message: text,
        topicId: widget.topicId,
      );
      final msg = _Message.fromResponse(response);
      setState(() => _messages.add(msg));
      _saveHistory();
    } catch (e) {
      setState(() => _messages.add(_Message(
        role: 'assistant',
        text: 'Failed to reach the tutor — check your connection.',
        isError: true,
      )));
      _saveHistory();
      // Also surface a snackbar for quick visibility
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(e.toString().replaceFirst('Exception: ', '')),
            backgroundColor: const Color(0xFF7F1D1D),
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    } finally {
      if (mounted) setState(() => _loading = false);
      _scrollToBottom();
    }
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent + 200,
          duration: const Duration(milliseconds: 350),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: _bg,
      appBar: AppBar(
        backgroundColor: _surface,
        foregroundColor: Colors.white,
        elevation: 0,
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Python Tutor',
                style: TextStyle(fontSize: 15, fontWeight: FontWeight.w700)),
            Text(widget.topicLabel,
                style: const TextStyle(fontSize: 12, color: Color(0xFF6B7280))),
          ],
        ),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_rounded, size: 18),
          onPressed: () => Navigator.pop(context),
        ),
        actions: [
          IconButton(
            onPressed: _clearHistory,
            icon: const Icon(Icons.delete_outline_rounded, size: 20),
            tooltip: 'Clear history',
          ),
          TextButton.icon(
            onPressed: () {
              _controller.text = 'give me the next activity';
              _send();
            },
            icon: const Icon(Icons.auto_fix_high_rounded, size: 16, color: _indigo),
            label: const Text('Next activity',
                style: TextStyle(color: _indigo, fontSize: 12)),
          ),
        ],
      ),
      body: Column(
        children: [
          // Message list
          Expanded(
            child: ListView.builder(
              controller: _scrollController,
              padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
              itemCount: _messages.length + (_loading ? 1 : 0),
              itemBuilder: (context, i) {
                if (i == _messages.length) return const _TypingBubble();
                return _ChatBubble(
                  message: _messages[i],
                  topicId: widget.topicId,
                );
              },
            ),
          ),

          // Quick-prompt chips (only at start)
          if (!_loading && _messages.length <= 1)
            _QuickPrompts(
              topicLabel: widget.topicLabel,
              onTap: (prompt) {
                _controller.text = prompt;
                _send();
              },
            ),

          // Input bar
          _InputBar(
            controller: _controller,
            loading: _loading,
            onSend: _send,
          ),
        ],
      ),
    );
  }
}

// ── Chat bubble ───────────────────────────────────────────────────────────

class _ChatBubble extends StatefulWidget {
  final _Message message;
  final String topicId;
  const _ChatBubble({super.key, required this.message, required this.topicId});

  @override
  State<_ChatBubble> createState() => _ChatBubbleState();
}

class _ChatBubbleState extends State<_ChatBubble> {
  bool _sourcesExpanded = false;
  String? _vote; // 'up', 'down', or null
  bool _submittingVote = false;

  Future<void> _submitVote(String rating) async {
    if (_vote != null || _submittingVote) return;
    setState(() => _submittingVote = true);
    
    try {
      await apiClient.submitTutorFeedback(
        topicId: widget.topicId,
        messageId: widget.message.id,
        rating: rating,
      );
      if (mounted) {
        setState(() => _vote = rating);
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Thanks for your feedback!'),
            backgroundColor: Color(0xFF10B981),
            behavior: SnackBarBehavior.floating,
            duration: Duration(seconds: 2),
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to submit feedback: $e'),
            backgroundColor: const Color(0xFF7F1D1D),
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _submittingVote = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final m      = widget.message;
    final isUser = m.role == 'user';

    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        mainAxisAlignment: isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          if (!isUser) ...[
            Container(
              width: 28,
              height: 28,
              decoration: const BoxDecoration(
                color: Color(0xFF6366F1),
                shape: BoxShape.circle,
              ),
              child: const Icon(Icons.smart_toy_rounded, color: Colors.white, size: 15),
            ),
            const SizedBox(width: 8),
          ],
          Flexible(
            child: Column(
              crossAxisAlignment:
                  isUser ? CrossAxisAlignment.end : CrossAxisAlignment.start,
              children: [
                // Main bubble
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                  decoration: BoxDecoration(
                    color: isUser
                        ? const Color(0xFF6366F1)
                        : m.isError
                            ? const Color(0xFF7F1D1D)
                            : const Color(0xFF1F2937),
                    borderRadius: BorderRadius.only(
                      topLeft:     const Radius.circular(16),
                      topRight:    const Radius.circular(16),
                      bottomLeft:  Radius.circular(isUser ? 16 : 4),
                      bottomRight: Radius.circular(isUser ? 4 : 16),
                    ),
                  ),
                  child: Text(
                    m.text,
                    style: TextStyle(
                      color: isUser ? Colors.white : const Color(0xFFE5E7EB),
                      fontSize: 14,
                      height: 1.5,
                    ),
                  ),
                ),

                // ── Assistant-only annotations ────────────────────────────
                if (!isUser) ...[
                  const SizedBox(height: 6),

                  // Pending-review pill
                  if (m.pendingReview)
                    _Pill(
                      icon: Icons.hourglass_top_rounded,
                      label: 'Your tutor\'s reviewing this recommendation',
                      color: const Color(0xFFFBBF24),
                    ),

                  // Risk tier badge (when auto-applied)
                  if (m.autoApplied && m.riskTier != null)
                    _Pill(
                      icon: Icons.check_circle_outline_rounded,
                      label: 'Auto-applied · ${m.riskTier} risk',
                      color: const Color(0xFF10B981),
                    ),

                  // Grounded indicator
                  if (m.grounded == true && m.sourceChunks != null && m.sourceChunks!.isNotEmpty)
                    _SourceAttribution(
                      chunks: m.sourceChunks!,
                      expanded: _sourcesExpanded,
                      onToggle: () =>
                          setState(() => _sourcesExpanded = !_sourcesExpanded),
                    ),

                  // Not grounded disclaimer
                  if (m.grounded == false)
                    _Pill(
                      icon: Icons.info_outline_rounded,
                      label: 'Not grounded in course material',
                      color: const Color(0xFF6B7280),
                    ),

                  // Thumbs up / down for feedback
                  if (!m.isError)
                    Padding(
                      padding: const EdgeInsets.only(top: 8),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          _FeedbackButton(
                            icon: Icons.thumb_up_alt_rounded,
                            isActive: _vote == 'up',
                            isDisabled: _vote != null,
                            onTap: () => _submitVote('up'),
                          ),
                          const SizedBox(width: 8),
                          _FeedbackButton(
                            icon: Icons.thumb_down_alt_rounded,
                            isActive: _vote == 'down',
                            isDisabled: _vote != null,
                            onTap: () => _submitVote('down'),
                          ),
                        ],
                      ),
                    ),
                ],
              ],
            ),
          ),
          if (isUser) const SizedBox(width: 8),
        ],
      ),
    );
  }
}

// ── Source attribution widget ─────────────────────────────────────────────

class _SourceAttribution extends StatelessWidget {
  final List<Map<String, dynamic>> chunks;
  final bool expanded;
  final VoidCallback onToggle;

  const _SourceAttribution({
    required this.chunks,
    required this.expanded,
    required this.onToggle,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onToggle,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 250),
        margin: const EdgeInsets.only(top: 4),
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
        decoration: BoxDecoration(
          color: const Color(0xFF1A2236),
          borderRadius: BorderRadius.circular(10),
          border: Border.all(color: const Color(0xFF2D3347)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(Icons.library_books_rounded,
                    size: 13, color: Color(0xFF6366F1)),
                const SizedBox(width: 5),
                Text(
                  'Sources (${chunks.length})',
                  style: const TextStyle(
                    color: Color(0xFF6366F1),
                    fontSize: 11,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(width: 4),
                Icon(
                  expanded
                      ? Icons.keyboard_arrow_up_rounded
                      : Icons.keyboard_arrow_down_rounded,
                  size: 14,
                  color: const Color(0xFF6366F1),
                ),
              ],
            ),
            if (expanded) ...[
              const SizedBox(height: 6),
              ...chunks.map((chunk) {
                final isInstructor = chunk['source_type'] == 'instructor_upload';
                return Padding(
                  padding: const EdgeInsets.only(bottom: 4),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        isInstructor ? '📎' : '📘',
                        style: const TextStyle(fontSize: 11),
                      ),
                      const SizedBox(width: 5),
                      Expanded(
                        child: Text(
                          '${chunk['heading'] ?? 'Section'}'
                          '${isInstructor ? ' · Instructor upload' : ' · Course material'}',
                          style: const TextStyle(
                            color: Color(0xFF9CA3AF),
                            fontSize: 11,
                            height: 1.4,
                          ),
                        ),
                      ),
                    ],
                  ),
                );
              }),
            ],
          ],
        ),
      ),
    );
  }
}

// ── Pill annotation ───────────────────────────────────────────────────────

class _Pill extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color color;

  const _Pill({required this.icon, required this.label, required this.color});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(top: 4),
      padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 4),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color.withValues(alpha: 0.3)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 12, color: color),
          const SizedBox(width: 5),
          Flexible(
            child: Text(
              label,
              style: TextStyle(
                color: color,
                fontSize: 11,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

// ── Typing indicator ──────────────────────────────────────────────────────

class _TypingBubble extends StatefulWidget {
  const _TypingBubble();

  @override
  State<_TypingBubble> createState() => _TypingBubbleState();
}

class _TypingBubbleState extends State<_TypingBubble>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 800),
    )..repeat(reverse: true);
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        children: [
          Container(
            width: 28,
            height: 28,
            decoration: const BoxDecoration(
              color: Color(0xFF6366F1),
              shape: BoxShape.circle,
            ),
            child: const Icon(Icons.smart_toy_rounded, color: Colors.white, size: 15),
          ),
          const SizedBox(width: 8),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
            decoration: BoxDecoration(
              color: const Color(0xFF1F2937),
              borderRadius: BorderRadius.circular(16),
            ),
            child: AnimatedBuilder(
              animation: _controller,
              builder: (_, __) => Row(
                mainAxisSize: MainAxisSize.min,
                children: List.generate(
                  3,
                  (i) => Padding(
                    padding: EdgeInsets.only(left: i == 0 ? 0 : 4),
                    child: Opacity(
                      opacity:
                          ((_controller.value + i * 0.3) % 1.0).clamp(0.2, 1.0),
                      child: const CircleAvatar(
                          radius: 4, backgroundColor: Color(0xFF6B7280)),
                    ),
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

// ── Quick-prompt chips ────────────────────────────────────────────────────

class _QuickPrompts extends StatelessWidget {
  final String topicLabel;
  final void Function(String) onTap;
  const _QuickPrompts({required this.topicLabel, required this.onTap});

  @override
  Widget build(BuildContext context) {
    final prompts = [
      'Explain $topicLabel with an example',
      'What are common mistakes with $topicLabel?',
      'Give me a challenge',
      'give me the next activity',
    ];
    return SizedBox(
      height: 44,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 16),
        itemCount: prompts.length,
        separatorBuilder: (_, __) => const SizedBox(width: 8),
        itemBuilder: (_, i) => ActionChip(
          label: Text(prompts[i], style: const TextStyle(fontSize: 12)),
          backgroundColor: const Color(0xFF1F2937),
          side: const BorderSide(color: Color(0xFF374151)),
          labelStyle: const TextStyle(color: Color(0xFFD1D5DB)),
          onPressed: () => onTap(prompts[i]),
        ),
      ),
    );
  }
}

// ── Input bar ─────────────────────────────────────────────────────────────

class _InputBar extends StatelessWidget {
  final TextEditingController controller;
  final bool loading;
  final VoidCallback onSend;
  const _InputBar(
      {required this.controller, required this.loading, required this.onSend});

  @override
  Widget build(BuildContext context) {
    return Container(
      color: const Color(0xFF141824),
      padding: const EdgeInsets.fromLTRB(16, 10, 16, 16),
      child: Row(
        children: [
          Expanded(
            child: TextField(
              controller: controller,
              style: const TextStyle(color: Colors.white, fontSize: 14),
              decoration: InputDecoration(
                hintText: 'Ask anything about Python…',
                hintStyle:
                    const TextStyle(color: Color(0xFF4B5563), fontSize: 14),
                filled: true,
                fillColor: const Color(0xFF1F2937),
                contentPadding:
                    const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide.none,
                ),
                enabled: !loading,
              ),
              onSubmitted: (_) => onSend(),
              maxLines: null,
              textInputAction: TextInputAction.send,
            ),
          ),
          const SizedBox(width: 10),
          AnimatedContainer(
            duration: const Duration(milliseconds: 200),
            width: 44,
            height: 44,
            decoration: BoxDecoration(
              color: loading ? const Color(0xFF374151) : const Color(0xFF6366F1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: IconButton(
              icon: loading
                  ? const SizedBox(
                      width: 18,
                      height: 18,
                      child: CircularProgressIndicator(
                          strokeWidth: 2, color: Colors.white))
                  : const Icon(Icons.send_rounded, color: Colors.white, size: 18),
              onPressed: loading ? null : onSend,
            ),
          ),
        ],
      ),
    );
  }
}

// ── Feedback button ───────────────────────────────────────────────────────

class _FeedbackButton extends StatelessWidget {
  final IconData icon;
  final bool isActive;
  final bool isDisabled;
  final VoidCallback onTap;

  const _FeedbackButton({
    required this.icon,
    required this.isActive,
    required this.isDisabled,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: isDisabled ? null : onTap,
      child: Container(
        padding: const EdgeInsets.all(6),
        decoration: BoxDecoration(
          color: isActive 
              ? const Color(0xFF6366F1).withValues(alpha: 0.2) 
              : Colors.transparent,
          borderRadius: BorderRadius.circular(6),
          border: Border.all(
            color: isActive 
                ? const Color(0xFF6366F1) 
                : (isDisabled ? Colors.transparent : const Color(0xFF2D3347)),
          ),
        ),
        child: Icon(
          icon,
          size: 16,
          color: isActive 
              ? const Color(0xFF6366F1) 
              : (isDisabled ? const Color(0xFF4B5563) : const Color(0xFF9CA3AF)),
        ),
      ),
    );
  }
}
