
create or replace function public.match_document_chunks(
    query_embedding extensions.vector(768),
    match_count integer default 5,
    filter_owner_id uuid default null,
    filter_document_id uuid default null
)
returns table (
    chunk_id uuid,
    document_id uuid,
    content text,
    metadata jsonb,
    similarity float
)
language sql
stable
security invoker
set search_path = ''
as $$
    select
        c.id,
        c.document_id,
        c.content,
        c.metadata,
        1 - (c.embedding OPERATOR(extensions.<=>) query_embedding)
            as similarity
    from public.document_chunks c
    join public.documents d
        on d.id = c.document_id
       and d.owner_id = c.owner_id
    where
        c.owner_id = (select auth.uid())
        and d.owner_id = (select auth.uid())
        and d.status = 'ready'
        and c.embedding is not null
        and (
            filter_owner_id is null
            or c.owner_id = filter_owner_id
        )
        and (
            filter_document_id is null
            or c.document_id = filter_document_id
        )
    order by
        c.embedding OPERATOR(extensions.<=>) query_embedding
    limit least(greatest(match_count, 1), 20);
$$;

grant execute on function public.match_document_chunks(
    extensions.vector,
    integer,
    uuid,
    uuid
) to authenticated;
