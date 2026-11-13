
-- Private knowledge document storage policies

create policy "Users upload to own document folder"
on storage.objects
for insert
to authenticated
with check (
    bucket_id = 'knowledge-documents'
    and (storage.foldername(name))[1] = (select auth.uid())::text
);

create policy "Users read own documents"
on storage.objects
for select
to authenticated
using (
    bucket_id = 'knowledge-documents'
    and (storage.foldername(name))[1] = (select auth.uid())::text
);

create policy "Users delete own documents"
on storage.objects
for delete
to authenticated
using (
    bucket_id = 'knowledge-documents'
    and (storage.foldername(name))[1] = (select auth.uid())::text
);
