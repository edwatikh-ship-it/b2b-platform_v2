export interface Request {
  id: number
  filename: string
  status: 'draft' | 'submitted' | 'moderation' | 'completed'
  items_count: number
  contacts_count: number
  created_at: string
}

export interface RequestItem {
  pos: number
  name: string
  unit: string
  qty: string | number
}

export interface Contact {
  supplier_name: string
  supplier_inn: string
  supplier_domain: string
  contact_name: string
  contact_phone: string
  contact_email: string
}

export interface ParsingTask {
  task_id: number
  request_id: number
  item_name: string
  search_query: string
  status: string
  created_at: string
}

export interface ParsedURL {
  id: number
  url: string
  title: string
  company_name: string
}

export interface Supplier {
  id: number
  domain: string
  company_name: string
  inn: string
  rating: number
}