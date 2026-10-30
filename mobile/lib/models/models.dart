// Data models mirroring backend/app/schemas.py. Kept as plain Dart classes
// (no code generation) so the file is readable without running build_runner.

class Customer {
  final String id;
  final String companyId;
  final String name;
  final String? contactName;
  final String? contactEmail;
  final String? contactPhone;
  final String? address;

  Customer({
    required this.id,
    required this.companyId,
    required this.name,
    this.contactName,
    this.contactEmail,
    this.contactPhone,
    this.address,
  });

  factory Customer.fromJson(Map<String, dynamic> json) => Customer(
        id: json['id'],
        companyId: json['company_id'],
        name: json['name'],
        contactName: json['contact_name'],
        contactEmail: json['contact_email'],
        contactPhone: json['contact_phone'],
        address: json['address'],
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'company_id': companyId,
        'name': name,
        'contact_name': contactName,
        'contact_email': contactEmail,
        'contact_phone': contactPhone,
        'address': address,
      };
}

class SiteModel {
  final String id;
  final String customerId;
  final String name;
  final String? address;

  SiteModel({required this.id, required this.customerId, required this.name, this.address});

  factory SiteModel.fromJson(Map<String, dynamic> json) => SiteModel(
        id: json['id'],
        customerId: json['customer_id'],
        name: json['name'],
        address: json['address'],
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'customer_id': customerId,
        'name': name,
        'address': address,
      };
}

class Equipment {
  final String id;
  final String siteId;
  final String manufacturer;
  final String model;
  final String? serialNumber;
  final String? category;
  final String? firmwareVersion;

  Equipment({
    required this.id,
    required this.siteId,
    required this.manufacturer,
    required this.model,
    this.serialNumber,
    this.category,
    this.firmwareVersion,
  });

  factory Equipment.fromJson(Map<String, dynamic> json) => Equipment(
        id: json['id'],
        siteId: json['site_id'],
        manufacturer: json['manufacturer'],
        model: json['model'],
        serialNumber: json['serial_number'],
        category: json['category'],
        firmwareVersion: json['firmware_version'],
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'site_id': siteId,
        'manufacturer': manufacturer,
        'model': model,
        'serial_number': serialNumber,
        'category': category,
        'firmware_version': firmwareVersion,
      };
}

enum WorkOrderStatus {
  open,
  assigned,
  inProgress,
  waitingForParts,
  pendingCustomer,
  completed,
  closed,
}

WorkOrderStatus statusFromString(String value) {
  switch (value) {
    case 'open':
      return WorkOrderStatus.open;
    case 'assigned':
      return WorkOrderStatus.assigned;
    case 'in_progress':
      return WorkOrderStatus.inProgress;
    case 'waiting_for_parts':
      return WorkOrderStatus.waitingForParts;
    case 'pending_customer':
      return WorkOrderStatus.pendingCustomer;
    case 'completed':
      return WorkOrderStatus.completed;
    case 'closed':
      return WorkOrderStatus.closed;
    default:
      return WorkOrderStatus.open;
  }
}

String statusToString(WorkOrderStatus status) {
  switch (status) {
    case WorkOrderStatus.open:
      return 'open';
    case WorkOrderStatus.assigned:
      return 'assigned';
    case WorkOrderStatus.inProgress:
      return 'in_progress';
    case WorkOrderStatus.waitingForParts:
      return 'waiting_for_parts';
    case WorkOrderStatus.pendingCustomer:
      return 'pending_customer';
    case WorkOrderStatus.completed:
      return 'completed';
    case WorkOrderStatus.closed:
      return 'closed';
  }
}

class WorkOrder {
  final String id;
  final String companyId;
  final String customerId;
  final String siteId;
  final String? equipmentId;
  final String title;
  final String? description;
  final WorkOrderStatus status;
  final String priority;
  final String? assignedEngineerId;
  final DateTime updatedAt;
  // Local-only: true while this record has edits not yet confirmed by the server.
  final bool pendingSync;

  WorkOrder({
    required this.id,
    required this.companyId,
    required this.customerId,
    required this.siteId,
    this.equipmentId,
    required this.title,
    this.description,
    required this.status,
    required this.priority,
    this.assignedEngineerId,
    required this.updatedAt,
    this.pendingSync = false,
  });

  factory WorkOrder.fromJson(Map<String, dynamic> json, {bool pendingSync = false}) => WorkOrder(
        id: json['id'],
        companyId: json['company_id'],
        customerId: json['customer_id'],
        siteId: json['site_id'],
        equipmentId: json['equipment_id'],
        title: json['title'],
        description: json['description'],
        status: statusFromString(json['status']),
        priority: json['priority'],
        assignedEngineerId: json['assigned_engineer_id'],
        updatedAt: DateTime.parse(json['updated_at']),
        pendingSync: pendingSync,
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'company_id': companyId,
        'customer_id': customerId,
        'site_id': siteId,
        'equipment_id': equipmentId,
        'title': title,
        'description': description,
        'status': statusToString(status),
        'priority': priority,
        'assigned_engineer_id': assignedEngineerId,
        'updated_at': updatedAt.toIso8601String(),
      };
}

enum ServiceNoteType { initialCondition, investigation, outcome, followUp, general }

String noteTypeToString(ServiceNoteType type) {
  switch (type) {
    case ServiceNoteType.initialCondition:
      return 'initial_condition';
    case ServiceNoteType.investigation:
      return 'investigation';
    case ServiceNoteType.outcome:
      return 'outcome';
    case ServiceNoteType.followUp:
      return 'follow_up';
    case ServiceNoteType.general:
      return 'general';
  }
}

class ServiceNote {
  final String id;
  final String workOrderId;
  final ServiceNoteType noteType;
  final String content;
  final DateTime createdAt;

  ServiceNote({
    required this.id,
    required this.workOrderId,
    required this.noteType,
    required this.content,
    required this.createdAt,
  });

  Map<String, dynamic> toJson() => {
        'id': id,
        'work_order_id': workOrderId,
        'note_type': noteTypeToString(noteType),
        'content': content,
      };
}
