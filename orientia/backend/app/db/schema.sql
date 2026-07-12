-- OrientIA schema — run this in the Supabase SQL editor.
-- Enables pgvector and creates all core tables.

create extension if not exists vector;

-- ============ Users profile (extends Supabase auth.users) ============
create table if not exists profiles (
    id uuid primary key references auth.users(id) on delete cascade,
    full_name text,
    filiere text,               -- e.g. "PCSI", "Bac SM", "Prépa ECG"
    average_grade numeric(4,2), -- out of 20
    languages jsonb default '[]',
    target_intake text,          -- e.g. "2026-09"
    created_at timestamptz default now()
);

-- ============ Programs (ingested from Campus France / Parcoursup / university sites) ============
create table if not exists programs (
    id bigint generated always as identity primary key,
    source text not null,               -- 'campus_france' | 'parcoursup' | 'university'
    source_url text,
    university text not null,
    program_name text not null,
    degree_level text,                  -- 'L1' | 'L2' | 'L3' | 'M1' | 'M2'
    field text,                          -- e.g. "Computer Science"
    city text,
    country text default 'France',
    tuition_eur numeric,
    language_of_instruction text,
    min_average_required numeric(4,2),
    application_deadline date,
    requirements_raw text,              -- full scraped text, chunked below
    requirements_summary text,          -- short AI-generated summary
    created_at timestamptz default now(),
    updated_at timestamptz default now()
);

-- ============ Vector chunks for RAG retrieval over program requirements ============
create table if not exists program_chunks (
    id bigint generated always as identity primary key,
    program_id bigint references programs(id) on delete cascade,
    chunk_text text not null,
    embedding vector(384),
    created_at timestamptz default now()
);

-- ANN index for fast cosine similarity search
create index if not exists program_chunks_embedding_idx
    on program_chunks using ivfflat (embedding vector_cosine_ops)
    with (lists = 100);

-- Similarity search function called from the RAG service
create or replace function match_program_chunks (
    query_embedding vector(384),
    match_count int default 8,
    filter_country text default null
)
returns table (
    program_id bigint,
    chunk_text text,
    similarity float
)
language sql stable
as $$
    select
        pc.program_id,
        pc.chunk_text,
        1 - (pc.embedding <=> query_embedding) as similarity
    from program_chunks pc
    join programs p on p.id = pc.program_id
    where filter_country is null or p.country = filter_country
    order by pc.embedding <=> query_embedding
    limit match_count;
$$;

-- ============ Applications (Kanban board) ============
create table if not exists applications (
    id bigint generated always as identity primary key,
    user_id uuid references profiles(id) on delete cascade,
    program_id bigint references programs(id) on delete cascade,
    status text not null default 'considering',
        -- 'considering' | 'in_progress' | 'submitted' | 'interview' | 'accepted' | 'rejected'
    motivation_letter_draft text,
    missing_documents jsonb default '[]',
    notes text,
    created_at timestamptz default now(),
    updated_at timestamptz default now(),
    unique (user_id, program_id)
);

-- ============ Uploaded transcripts + extracted data ============
create table if not exists transcripts (
    id bigint generated always as identity primary key,
    user_id uuid references profiles(id) on delete cascade,
    file_name text,
    extracted_grades jsonb,      -- [{subject, grade, coefficient, year}]
    flagged_weak_spots jsonb,    -- [{subject, issue, suggestion}]
    raw_text text,
    created_at timestamptz default now()
);

-- Row-level security (every user only sees their own rows)
alter table profiles enable row level security;
alter table applications enable row level security;
alter table transcripts enable row level security;

create policy "own profile" on profiles for all using (auth.uid() = id);
create policy "own applications" on applications for all using (auth.uid() = user_id);
create policy "own transcripts" on transcripts for all using (auth.uid() = user_id);

-- Programs are public read (catalog data), writes go through the service key only
alter table programs enable row level security;
create policy "public read programs" on programs for select using (true);
