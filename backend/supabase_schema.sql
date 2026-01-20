-- ==========================================
-- 1. DOCUMENTS TABLE
-- ==========================================

create table if not exists documents (
  id uuid default gen_random_uuid() primary key,
  user_id uuid, -- Make nullable just in case
  filename text,
  storage_path text,
  job_id text, 
  upload_time timestamptz default now(),
  created_at timestamptz default now()
);

-- Enable RLS but add permissive policies
alter table documents enable row level security;

-- DROP EXISTING POLICIES TO AVOID CONFLICTS
drop policy if exists "Users can insert their own documents" on documents;
drop policy if exists "Users can view their own documents" on documents;
drop policy if exists "Users can delete their own documents" on documents;
drop policy if exists "Allow public insert" on documents;
drop policy if exists "Allow public select" on documents;
drop policy if exists "Allow public delete" on documents;

-- PERMISSIVE POLICIES (Fixes 403 Unauthorized for local dev)
create policy "Allow public insert"
  on documents for insert
  with check (true);

create policy "Allow public select"
  on documents for select
  using (true);

create policy "Allow public delete"
  on documents for delete
  using (true);


-- ==========================================
-- 2. CHATS TABLE
-- ==========================================

create table if not exists chats (
  id uuid default gen_random_uuid() primary key,
  user_id uuid,
  document_id text,
  question text,
  answer text,
  created_at timestamptz default now()
);

alter table chats enable row level security;

-- DROP EXISTING POLICIES
drop policy if exists "Users can insert their own chats" on chats;
drop policy if exists "Users can view their own chats" on chats;
drop policy if exists "Allow public insert" on chats;
drop policy if exists "Allow public select" on chats;

-- PERMISSIVE POLICIES
create policy "Allow public insert"
  on chats for insert
  with check (true);

create policy "Allow public select"
  on chats for select
  using (true);


-- ==========================================
-- 3. STORAGE SETUP
-- ==========================================

-- Ensure bucket exists
insert into storage.buckets (id, name, public) 
values ('documents', 'documents', true) -- Set public to true
on conflict (id) do update set public = true;

-- DROP OLD STORAGE POLICIES
drop policy if exists "Allow authenticated uploads" on storage.objects;
drop policy if exists "Allow authenticated viewing" on storage.objects;
drop policy if exists "Allow authenticated delete" on storage.objects;
drop policy if exists "Allow public uploads" on storage.objects;
drop policy if exists "Allow public viewing" on storage.objects;
drop policy if exists "Allow public delete" on storage.objects;

-- NEW PERMISSIVE STORAGE POLICIES
create policy "Allow public uploads"
on storage.objects for insert
with check ( bucket_id = 'documents' );

create policy "Allow public viewing"
on storage.objects for select
using ( bucket_id = 'documents' );

create policy "Allow public delete"
on storage.objects for delete
using ( bucket_id = 'documents' );
