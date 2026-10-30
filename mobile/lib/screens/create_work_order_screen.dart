import 'package:flutter/material.dart';

import '../services/api_client.dart';

class CreateWorkOrderScreen extends StatefulWidget {
  final ApiClient api;
  final String customerId;
  final String siteId;

  const CreateWorkOrderScreen({
    super.key,
    required this.api,
    required this.customerId,
    required this.siteId,
  });

  @override
  State<CreateWorkOrderScreen> createState() => _CreateWorkOrderScreenState();
}

class _CreateWorkOrderScreenState extends State<CreateWorkOrderScreen> {
  final _titleController = TextEditingController();
  final _descriptionController = TextEditingController();
  String _priority = 'normal';
  bool _saving = false;
  String? _error;

  Future<void> _submit() async {
    if (_titleController.text.trim().isEmpty) {
      setState(() => _error = 'Title is required.');
      return;
    }
    setState(() {
      _saving = true;
      _error = null;
    });
    try {
      await widget.api.createWorkOrder({
        'customer_id': widget.customerId,
        'site_id': widget.siteId,
        'title': _titleController.text.trim(),
        'description': _descriptionController.text.trim(),
        'priority': _priority,
      });
      if (!mounted) return;
      Navigator.of(context).pop(true);
    } catch (e) {
      setState(() => _error = 'Could not create work order. Try again when online.');
    } finally {
      setState(() => _saving = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('New Work Order')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            TextField(
              controller: _titleController,
              decoration: const InputDecoration(labelText: 'Title'),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: _descriptionController,
              decoration: const InputDecoration(labelText: 'Description'),
              maxLines: 3,
            ),
            const SizedBox(height: 12),
            DropdownButton<String>(
              value: _priority,
              items: const [
                DropdownMenuItem(value: 'low', child: Text('Low')),
                DropdownMenuItem(value: 'normal', child: Text('Normal')),
                DropdownMenuItem(value: 'high', child: Text('High')),
                DropdownMenuItem(value: 'urgent', child: Text('Urgent')),
              ],
              onChanged: (value) => setState(() => _priority = value ?? 'normal'),
            ),
            const SizedBox(height: 16),
            if (_error != null) Text(_error!, style: const TextStyle(color: Colors.red)),
            ElevatedButton(
              onPressed: _saving ? null : _submit,
              child: _saving ? const CircularProgressIndicator() : const Text('Create Work Order'),
            ),
          ],
        ),
      ),
    );
  }
}
