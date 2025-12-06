# Fork Stack Implementation Plan

## Hybrid Structure (Adopted)

```
fork-stack/
├── templates/
│   ├── base/                      # Core pattern by language
│   │   ├── python/
│   │   ├── go/
│   │   ├── typescript/
│   │   └── rust/
│   │
│   └── implementations/           # Pluggable backends
│       ├── databases/             # Phase 1
│       │   ├── turso/
│       │   ├── neon/
│       │   └── planetscale/
│       ├── storage/               # Phase 1
│       │   ├── tigris/
│       │   ├── s3/
│       │   └── r2/
│       ├── secrets/               # Phase 1
│       │   ├── doppler/
│       │   ├── aws-secrets/
│       │   └── vault/
│       ├── cache/                 # Phase 3
│       │   ├── upstash-redis/
│       │   ├── redis-cloud/
│       │   └── valkey/
│       └── queue/                 # Phase 3
│           ├── upstash-qstash/
│           ├── inngest/
│           └── bullmq/
│
├── stacks/                        # Pre-configured combinations
│   ├── python-turso-tigris-doppler/
│   ├── go-neon-s3-vault/
│   └── typescript-planetscale-r2-doppler/
│
└── examples/                      # Full working examples
    └── python-turso-tigris-doppler/
```

## Phase 1: Restructure Python Templates ✅ NEXT

### Goal
Extract current monolithic Python templates into modular base + implementations.

### Tasks

**1. Create base Python template**
```
templates/base/python/
├── README.md              # Pattern explanation
├── env_utils.py           # Abstract base with plugin points
├── Makefile.base          # Core make commands
└── .gitignore             # Standard ignores
```

**Key file: `env_utils.py`**
```python
# Abstract base - implementations fill in the blanks
class EnvConfig:
    def get_current_env(self) -> str:
        """Read .current-env or default to 'dev'"""
        # Core implementation (same for all)

    # Plugin points - implemented by backends
    def get_database_url(self) -> str:
        raise NotImplementedError("Implement in your stack")

    def get_bucket_name(self) -> str:
        raise NotImplementedError("Implement in your stack")

    def get_secret(self, key: str) -> str:
        raise NotImplementedError("Implement in your stack")
```

**2. Extract Turso implementation**
```
templates/implementations/databases/turso/
├── README.md              # Turso setup & CLI guide
├── python.py              # Python implementation
└── cli-commands.txt       # Turso CLI reference
```

**Key file: `python.py`**
```python
"""Turso database implementation for Fork Stack."""

def get_database_url(project_name: str, env: str) -> str:
    """Get Turso database URL for environment."""
    if env == 'prod':
        return f'libsql://{project_name}.turso.io'
    return f'libsql://{project_name}-{env}.turso.io'

def create_branch(project_name: str, env: str) -> bool:
    """Create Turso database branch."""
    # Implementation

def delete_branch(project_name: str, env: str) -> bool:
    """Delete Turso database branch."""
    # Implementation
```

**3. Extract Tigris implementation**
```
templates/implementations/storage/tigris/
├── README.md              # Tigris setup & bucket forking
├── python.py              # Python implementation
└── setup-guide.md         # Tigris account setup
```

**4. Extract Doppler implementation**
```
templates/implementations/secrets/doppler/
├── README.md              # Doppler setup & CLI guide
├── python.py              # Python implementation
└── setup-guide.md         # Doppler account setup
```

**5. Create python-turso-tigris-doppler stack**
```
stacks/python-turso-tigris-doppler/
├── README.md              # Quick start guide
├── env_utils.py           # Merged implementation
├── envs.py                # CLI tool with Turso + Tigris + Doppler
├── Makefile               # Complete Makefile
└── test_env_utils.py      # Tests
```

This is the "batteries included" version - copy this entire directory to your project and it works.

**6. Update documentation**
- Move current README content to `stacks/python-turso-tigris-doppler/README.md`
- Create new main README with structure overview
- Add `docs/choosing-a-stack.md` decision tree

### Success Criteria
- [ ] Can copy `stacks/python-turso-tigris-doppler/` and it works
- [ ] Can mix `base/python/` + `implementations/*/python.py` manually
- [ ] All existing examples still work
- [ ] Tests pass

---

## Phase 2: Add Alternative Python Backends

### Goal
Demonstrate plugin architecture with 2-3 popular alternatives.

### Priority Stacks

**1. python-neon-s3**
- Postgres developers
- AWS ecosystem users
- Most requested alternative

**2. python-supabase-tigris**
- Postgres + realtime features
- Cost-conscious (Tigris cheaper than S3)
- Growing popularity

**3. python-planetscale-r2**
- MySQL developers
- Cloudflare ecosystem users
- Edge computing focus

### Tasks per Stack

For each stack:
1. Create `implementations/databases/{db}/python.py`
2. Create `implementations/storage/{storage}/python.py`
3. Create `stacks/python-{db}-{storage}/`
4. Write setup guide in `docs/stacks/python-{db}-{storage}.md`
5. Add to comparison table in docs

### Backend Implementation Template

Each backend needs:
- `README.md` - Setup, prerequisites, account creation
- `python.py` - Implementation functions
- `cli-commands.txt` - Quick reference

Example structure:
```python
# implementations/databases/neon/python.py
def get_database_url(project_name: str, env: str) -> str:
    """Neon-specific URL generation."""

def create_branch(project_name: str, env: str, from_branch: str = 'main') -> bool:
    """Create Neon database branch."""

def delete_branch(project_name: str, env: str) -> bool:
    """Delete Neon database branch."""
```

### Success Criteria
- [ ] 3 working alternative stacks
- [ ] Documentation for each
- [ ] Comparison table shows tradeoffs
- [ ] Community can easily add more

---

## Phase 3: Add Cache + Queue Support

### Goal
Expand beyond core infrastructure to common development needs.

### New Categories

**Cache**
- Upstash Redis (recommended - serverless, per-env databases)
- Redis Cloud
- Valkey

**Queue/Jobs**
- Upstash QStash (recommended - serverless, HTTP-based)
- Inngest
- BullMQ + Redis

### Tasks

**1. Add cache implementations**
```
templates/implementations/cache/
├── upstash-redis/
│   ├── README.md
│   ├── python.py
│   └── setup-guide.md
├── redis-cloud/
└── valkey/
```

**2. Add queue implementations**
```
templates/implementations/queue/
├── upstash-qstash/
│   ├── README.md
│   ├── python.py
│   └── setup-guide.md
├── inngest/
└── bullmq/
```

**3. Update existing stacks**

Add cache + queue to existing stacks:
- `stacks/python-turso-tigris-doppler/` → add Upstash Redis + QStash
- Optional: Create new stacks for different combinations

**4. Update env_utils pattern**

Add to base template:
```python
class EnvConfig:
    # Existing methods...

    def get_cache_url(self) -> str:
        """Get environment-specific cache URL."""
        raise NotImplementedError

    def get_queue_url(self) -> str:
        """Get environment-specific queue URL."""
        raise NotImplementedError
```

**5. Update envs.py**

Add commands:
```python
def create_cache(env_name):
    """Create cache instance for environment."""

def create_queue(env_name):
    """Create queue instance for environment."""
```

### Success Criteria
- [ ] Working cache implementation (Upstash Redis)
- [ ] Working queue implementation (Upstash QStash)
- [ ] Updated stacks include cache + queue
- [ ] Documentation covers cache + queue setup

---

## Phase 4: Add Go Support

### Goal
First non-Python language to prove multi-language support works.

### Tasks

**1. Create Go base template**
```
templates/base/go/
├── README.md
├── env_utils.go           # Core utilities
├── Makefile.base
└── go.mod
```

**2. Implement Turso + Tigris in Go**
```
templates/implementations/databases/turso/
├── go.go                  # Go implementation

templates/implementations/storage/tigris/
├── go.go                  # Go implementation
```

**3. Create go-turso-tigris stack**
```
stacks/go-turso-tigris/
├── README.md
├── cmd/envs/main.go       # CLI tool
├── env_utils.go           # Merged implementation
├── Makefile
└── go.mod
```

**4. Document Go patterns**
- Add `docs/languages/go.md`
- Explain Go-specific patterns
- Reference Go example

### Success Criteria
- [ ] Working go-turso-tigris stack
- [ ] Go-specific documentation
- [ ] At least one example app

---

## Phase 5: Add TypeScript Support

### Goal
Support Node.js/TypeScript developers (large audience).

### Tasks

**1. Create TypeScript base template**
```
templates/base/typescript/
├── README.md
├── envUtils.ts            # Core utilities
├── Makefile.base
└── package.json
```

**2. Popular stack: typescript-neon-s3**

Most Node developers use:
- Postgres (Neon)
- AWS S3
- Node-native solutions

**3. Optional: npm package**
```bash
npm install fork-stack
```

Provides base utilities, implementations can be composed.

### Success Criteria
- [ ] Working TypeScript stack
- [ ] npm package (optional)
- [ ] TypeScript-specific docs

---

## Phase 6: Community & Ecosystem

### Goal
Make it easy for community to contribute new languages and backends.

### Tasks

**1. Contribution guidelines**
- `CONTRIBUTING.md` with templates
- Backend implementation checklist
- Stack creation guide
- Testing requirements

**2. Backend request system**
- GitHub issue templates
- "Request a backend" form
- "Request a language" form

**3. Community stacks**
```
stacks/community/
├── rust-turso-tigris/     # Community contributed
├── elixir-supabase-r2/
└── ...
```

**4. CLI scaffolding tool (optional)**
```bash
npx create-fork-stack
# Interactive prompts:
# - Language? (python/go/typescript/rust)
# - Database? (turso/neon/planetscale/supabase)
# - Storage? (tigris/s3/r2)
# - Secrets? (doppler/aws/vault/none)
#
# Downloads appropriate stack to ./
```

### Success Criteria
- [ ] At least 3 community contributions
- [ ] Clear contribution docs
- [ ] Active issue/discussion

---

## Naming Conventions

### Stacks
Format: `{language}-{database}-{storage}-{secrets}`
- `python-turso-tigris-doppler`
- `go-neon-s3-vault`
- `typescript-planetscale-r2-doppler`

Optional: Add cache/queue when they become standard:
- `python-turso-tigris-doppler` (minimal)
- `python-turso-tigris-doppler-redis-qstash` (full stack)

### Implementation Files
- `python.py`
- `go.go`
- `typescript.ts`
- `rust.rs`

### Directories
- Languages: lowercase (python, go, typescript)
- Backends: lowercase (turso, neon, tigris, s3)
- Stacks: lowercase with hyphens

---

## Documentation Structure

```
docs/
├── languages/
│   ├── python.md          # Python-specific guide
│   ├── go.md
│   └── typescript.md
│
├── backends/
│   ├── databases.md       # Database comparison
│   ├── storage.md         # Storage comparison
│   └── secrets.md         # Secrets manager comparison
│
├── stacks/
│   ├── choosing.md        # Decision tree
│   ├── python-turso-tigris.md
│   ├── go-neon-s3.md
│   └── ...
│
└── contributing/
    ├── add-language.md
    ├── add-backend.md
    └── add-stack.md
```

---

## Testing Strategy

Each stack must include:

1. **Unit tests** - Test utility functions
2. **Integration test** - Create/switch/delete environment
3. **Example app** - Minimal working application

Example test structure:
```
stacks/python-turso-tigris/
├── test_env_utils.py      # Unit tests
├── test_integration.py    # E2E test
└── example/
    └── app.py             # Minimal demo app
```

---

## Migration Path

### For Current Users

Current templates remain in place but marked as deprecated:
```
templates/
├── env_utils.py           # DEPRECATED: Use stacks/python-turso-tigris/
├── envs.py                # DEPRECATED: Use stacks/python-turso-tigris/
└── ...
```

README shows migration path:
```markdown
## Migrating from Old Structure

If you previously copied from `templates/`:

**Old:**
```bash
cp templates/env_utils.py your-project/
```

**New (Option 1 - Pre-built stack):**
```bash
cp stacks/python-turso-tigris/* your-project/
```

**New (Option 2 - Custom composition):**
```bash
cp templates/base/python/env_utils.py your-project/
cp templates/implementations/databases/neon/python.py your-project/
cp templates/implementations/storage/s3/python.py your-project/
# Merge implementations into env_utils.py
```
```

---

## Implementation Timeline

**Phase 1** - Core Python stack (database, storage, secrets)
**Phase 2** - Alternative Python backends (Neon, Supabase, PlanetScale)
**Phase 3** - Cache + Queue support (Upstash Redis, QStash)
**Phase 4** - Go language support
**Phase 5** - TypeScript language support
**Phase 6** - Community & ecosystem

## Next Steps

1. **Start Phase 1** - Restructure existing Python templates
2. **Get feedback** - Share with early users
3. **Iterate** - Refine based on feedback
4. **Continue phases** - Add backends, cache/queue, languages, community features

## Open Questions

1. **Package managers?** Should we publish:
   - `pip install fork-stack`
   - `npm install fork-stack`
   - `go get github.com/russellromney/fork-stack`

2. **Versioning?** How to handle breaking changes in backends?
   - Semantic versioning per stack?
   - Lock to backend version?

3. **Secrets priority?** Which secrets managers to support first?
   - Doppler (current)
   - AWS Secrets Manager
   - HashiCorp Vault
   - Just env files?
