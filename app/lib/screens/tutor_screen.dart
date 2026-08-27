import 'package:flutter/material.dart';
import '../services/api_client.dart';

class TutorScreen extends StatefulWidget {
  final String topicId;
  final String topicLabel;
  const TutorScreen({super.key, required this.topicId, required this.topicLabel});

  @override
  State<TutorScreen> createState() => _TutorScreenState();
}

class _TutorScreenState extends State<TutorScreen> {
  final _controller = TextEditingController();
  final _scrollController = ScrollController();
  final List<_Message> _messages = [];
  bool _loading = false;

  static const _indigo = Color(0xFF6366F1);
  static const _bg = Color(0xFF0A0E1A);
  static const _surface = Color(0xFF141824);

  @override
  void initState() {
    super.initState();
    // Greet with a Socratic prompt
    _messages.add(_Message(
      role: 'assistant',
      text: 'Hi! I\'m your Python tutor for **${widget.topicLabel}**. '
          'Ask me anything — or type "give me the next activity" and I\'ll '
          'suggest what to practice next.',
    ));
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
    _controller.clear();
    _scrollToBottom();

    try {
      final response = await apiClient.tutorChat(
        message: text,
        topicId: widget.topicId,
      );
      final reply = (response['response'] ??
              response['message'] ??
              response['content'] ??
              'No response from tutor.')
          .toString();
      setState(() {
        _messages.add(_Message(role: 'assistant', text: reply));
      });
    } catch (e) {
      setState(() {
        _messages.add(_Message(
          role: 'assistant',
          text: '⚠️ Error: ${e.toString().replaceFirst('Exception: ', '')}',
          isError: true,
        ));
      });
    } finally {
      setState(() => _loading = false);
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
                style: const TextStyle(
                    fontSize: 12, color: Color(0xFF6B7280))),
          ],
        ),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_rounded, size: 18),
          onPressed: () => Navigator.pop(context),
        ),
        actions: [
          TextButton.icon(
            onPressed: () {
              _controller.text = 'give me the next activity';
              _send();
            },
            icon: const Icon(Icons.auto_fix_high_rounded,
                size: 16, color: _indigo),
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
                if (i == _messages.length) {
                  return const _TypingBubble();
                }
                return _ChatBubble(message: _messages[i]);
              },
            ),
          ),

          // Quick-prompt chips
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

// ---------------------------------------------------------------------------
// Message model
// ---------------------------------------------------------------------------

class _Message {
  final String role; // 'user' | 'assistant'
  final String text;
  final bool isError;
  const _Message({required this.role, required this.text, this.isError = false});
}

// ---------------------------------------------------------------------------
// Chat bubble
// ---------------------------------------------------------------------------

class _ChatBubble extends StatelessWidget {
  final _Message message;
  const _ChatBubble({super.key, required this.message});

  @override
  Widget build(BuildContext context) {
    final isUser = message.role == 'user';
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        mainAxisAlignment:
            isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
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
              child:
                  const Icon(Icons.smart_toy_rounded, color: Colors.white, size: 15),
            ),
            const SizedBox(width: 8),
          ],
          Flexible(
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
              decoration: BoxDecoration(
                color: isUser
                    ? const Color(0xFF6366F1)
                    : message.isError
                        ? const Color(0xFF7F1D1D)
                        : const Color(0xFF1F2937),
                borderRadius: BorderRadius.only(
                  topLeft: const Radius.circular(16),
                  topRight: const Radius.circular(16),
                  bottomLeft: Radius.circular(isUser ? 16 : 4),
                  bottomRight: Radius.circular(isUser ? 4 : 16),
                ),
              ),
              child: Text(
                message.text,
                style: TextStyle(
                  color: isUser ? Colors.white : const Color(0xFFE5E7EB),
                  fontSize: 14,
                  height: 1.5,
                ),
              ),
            ),
          ),
          if (isUser) const SizedBox(width: 8),
        ],
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// Typing indicator
// ---------------------------------------------------------------------------

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
            child: const Icon(Icons.smart_toy_rounded,
                color: Colors.white, size: 15),
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
                      opacity: ((_controller.value + i * 0.3) % 1.0)
                          .clamp(0.2, 1.0),
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

// ---------------------------------------------------------------------------
// Quick-prompt chips
// ---------------------------------------------------------------------------

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

// ---------------------------------------------------------------------------
// Input bar
// ---------------------------------------------------------------------------

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
                hintStyle: const TextStyle(color: Color(0xFF4B5563), fontSize: 14),
                filled: true,
                fillColor: const Color(0xFF1F2937),
                contentPadding: const EdgeInsets.symmetric(
                    horizontal: 16, vertical: 12),
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
              color: loading
                  ? const Color(0xFF374151)
                  : const Color(0xFF6366F1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: IconButton(
              icon: loading
                  ? const SizedBox(
                      width: 18,
                      height: 18,
                      child: CircularProgressIndicator(
                          strokeWidth: 2, color: Colors.white))
                  : const Icon(Icons.send_rounded,
                      color: Colors.white, size: 18),
              onPressed: loading ? null : onSend,
            ),
          ),
        ],
      ),
    );
  }
}
