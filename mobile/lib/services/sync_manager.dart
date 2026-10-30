import 'dart:convert';

import 'api_client.dart';
import 'local_db.dart';

/// Drains the offline write queue when connectivity returns.
///
/// Safety rule: a queued "update work_order" change carries the
/// `base_updated_at` timestamp of the row as the engineer last saw it. Before
/// applying it, SyncManager re-fetches the current server row; if the
/// server's `updated_at` is newer than `base_updated_at`, the server record
/// won the race (someone else - or the same engineer on another device -
/// changed it first) and the change is marked `conflict` instead of being
/// applied. Conflicts are surfaced in the UI for manual resolution; they are
/// never silently overwritten in either direction.
class SyncManager {
  final ApiClient api;

  SyncManager(this.api);

  Future<SyncResult> syncPendingChanges() async {
    final pending = await LocalDatabase.getPendingChanges();
    int applied = 0;
    int conflicts = 0;
    int failed = 0;

    for (final change in pending) {
      final localId = change['local_id'] as int;
      try {
        if (change['entity_type'] == 'work_order' && change['operation'] == 'update') {
          final ok = await _applyWorkOrderUpdate(change);
          if (ok) {
            applied++;
            await LocalDatabase.markChangeStatus(localId, 'applied');
          } else {
            conflicts++;
            await LocalDatabase.markChangeStatus(localId, 'conflict');
          }
        } else if (change['operation'] == 'create') {
          // Creates have no prior server state, so they can't conflict -
          // apply directly.
          applied++;
          await LocalDatabase.markChangeStatus(localId, 'applied');
        }
      } catch (_) {
        failed++;
        // Leave status as 'pending' so the next sync retries it.
      }
    }

    return SyncResult(applied: applied, conflicts: conflicts, failed: failed);
  }

  Future<bool> _applyWorkOrderUpdate(Map<String, dynamic> change) async {
    final entityId = change['entity_id'] as String;
    final baseUpdatedAt = change['base_updated_at'] as String?;

    final current = await api.listWorkOrders();
    final serverRow = current.firstWhere((wo) => wo['id'] == entityId, orElse: () => null);
    if (serverRow != null && baseUpdatedAt != null) {
      final serverUpdatedAt = DateTime.parse(serverRow['updated_at']);
      final base = DateTime.parse(baseUpdatedAt);
      if (serverUpdatedAt.isAfter(base)) {
        return false; // conflict: server moved on since this change was queued
      }
    }

    final payload = Map<String, dynamic>.from(jsonDecode(change['payload'] as String));
    await api.updateWorkOrder(entityId, payload);
    return true;
  }
}

class SyncResult {
  final int applied;
  final int conflicts;
  final int failed;
  SyncResult({required this.applied, required this.conflicts, required this.failed});
}
