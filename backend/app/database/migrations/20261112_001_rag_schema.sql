
-- =========================================
-- RAG DOCUMENTS
-- =========================================

create table public.documents (
    id uuid primary key default gen_random_uuid(),

    owner_id uuid not null
        references auth.users(id)
        on delete cascade,

    title text not null,
    original_filename text not null,

    storage_path text not null unique,

    mime_type text not null,
    file_size_bytes bigint not null
        check (file_size_bytes > 0),

    status text not null default 'uploaded'
        check (
            status in (
                'uploaded',
                'processing',
                'ready',
                'failed'
            )
        ),

    error_message text,

    chunk_count integer not null default 0
        check (chunk_count >= 0),

    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);


-- =========================================
-- RAG DOCUMENT CHUNKS
-- Embedding model: nomic-embed-text
-- Dimensions: 768
-- =========================================

create table public.document_chunks (
    id uuid primary key default gen_random_uuid(),

    document_id uuid not null
        references public.documents(id)
        on delete cascade,

    owner_id uuid not null
        references auth.users(id)
        on delete cascade,

    chunk_index integer not null
        check (chunk_index >= 0),

    content text not null,

    embedding extensions.vector(768),

    metadata jsonb not null default '{}'::jsonb,

    created_at timestamptz not null default now(),

    unique (document_id, chunk_index)
);


-- =========================================
-- INDEXES
-- =========================================

create index documents_owner_idx
    on public.documents(owner_id);

create index documents_status_idx
    on public.documents(status);

create index chunks_document_idx
    on public.document_chunks(document_id);

create index chunks_owner_idx
    on public.document_chunks(owner_id);

create index chunks_metadata_idx
    on public.document_chunks
    using gin(metadata);


-- =========================================
-- VECTOR INDEX
-- =========================================

create index chunks_embedding_idx
    on public.document_chunks
    using hnsw (embedding extensions.vector_cosine_ops);


-- =========================================
-- ROW LEVEL SECURITY
-- =========================================

alter table public.documents
    enable row level security;

alter table public.document_chunks
    enable row level security;


-- Documents: owner can access their own documents

create policy "document_owner_select"
on public.documents
for select
to authenticated
using ((select auth.uid()) = owner_id);


create policy "document_owner_insert"
on public.documents
for insert
to authenticated
with check ((select auth.uid()) = owner_id);


create policy "document_owner_update"
on public.documents
for update
to authenticated
using ((select auth.uid()) = owner_id)
with check ((select auth.uid()) = owner_id);


create policy "document_owner_delete"
on public.documents
for delete
to authenticated
using ((select auth.uid()) = owner_id);


-- Chunks: owner can access their own chunks

create policy "chunk_owner_select"
on public.document_chunks
for select
to authenticated
using ((select auth.uid()) = owner_id);


create policy "chunk_owner_insert"
on public.document_chunks
for insert
to authenticated
with check ((select auth.uid()) = owner_id);


create policy "chunk_owner_update"
on public.document_chunks
for update
to authenticated
using ((select auth.uid()) = owner_id)
with check ((select auth.uid()) = owner_id);


create policy "chunk_owner_delete"
on public.document_chunks
for delete
to authenticated
using ((select auth.uid()) = owner_id);


-- =========================================
-- PERMISSIONS
-- =========================================

grant select, insert, update, delete
on public.documents
to authenticated;

grant select, insert, update, delete
on public.document_chunks
to authenticated;
