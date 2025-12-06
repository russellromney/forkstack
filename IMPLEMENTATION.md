# forkstack Implementation Plan

## Overview

forkstack is a CLI tool for creating instant, isolated development environments using database branching and storage forking.

## Architecture

```
forkstack/
├── cli/                    # CLI binary (forks command)
│   └── src/main.rs
├── forkstack/              # Core library
│   └── src/
│       ├── lib.rs          # Public API
│       ├── config.rs       # .forkstack.toml parsing
│       ├── turso.rs        # Turso API client
│       └── storage.rs      # S3/Tigris client
├── docs/                   # Documentation (MkDocs)
└── install.sh              # Installation script
```

## Core Concepts

### Configuration (.forkstack.toml)

```toml
[database]
provider = "turso"
organization = "your-org"
production = "my-app-prod"
group = "default"

[storage.uploads]
provider = "tigris"
bucket = "my-app-uploads"
endpoint = "https://fly.storage.tigris.dev"
prefix = "forks/"
```

### Commands

```bash
forks create           # Create fork with random name
forks create -n alice  # Create fork with specific name
forks list             # List all forks
forks delete alice     # Delete a fork
```

### What Happens

1. **forks create**:
   - Calls Turso API to create database branch (zero-copy)
   - Copies S3 objects to fork prefix (full copy)
   - Returns fork details (database URL, storage paths)

2. **forks list**:
   - Lists Turso databases matching fork pattern
   - Shows creation time and URLs

3. **forks delete**:
   - Deletes Turso database
   - Deletes all objects under fork prefix

---

## Phase 1: Core CLI ✅ COMPLETE

### Done
- [x] Rust workspace setup (cli + forkstack library)
- [x] Config parsing (.forkstack.toml)
- [x] Turso API client (create, list, delete databases)
- [x] S3/Tigris storage client (copy, delete objects)
- [x] CLI commands (create, list, delete)
- [x] Documentation site (MkDocs + Cloudflare Pages)

### Remaining
- [ ] Test CLI end-to-end with real credentials
- [ ] Error handling improvements
- [ ] Better output formatting

---

## Phase 2: Distribution

### Tasks
- [ ] Create install.sh script
- [ ] Publish to crates.io (`cargo install forkstack`)
- [ ] GitHub releases with prebuilt binaries
- [ ] Homebrew formula (optional)

### Install Script

```bash
#!/bin/bash
# Download prebuilt binary for platform
# Install to ~/.local/bin or /usr/local/bin
# Add to PATH if needed
```

---

## Phase 3: Additional Providers

### Database Providers
- [x] Turso (SQLite branching)
- [ ] Neon (Postgres branching)
- [ ] PlanetScale (MySQL branching)

### Storage Providers
- [x] Tigris (S3-compatible)
- [x] AWS S3
- [ ] Cloudflare R2

### Implementation Pattern

Each provider implements a trait:

```rust
pub trait DatabaseProvider {
    async fn create_fork(&self, name: &str, from: &str) -> Result<DatabaseInfo>;
    async fn list_forks(&self) -> Result<Vec<DatabaseInfo>>;
    async fn delete_fork(&self, name: &str) -> Result<()>;
}

pub trait StorageProvider {
    async fn copy_to_fork(&self, fork_name: &str) -> Result<String>;
    async fn delete_fork(&self, fork_name: &str) -> Result<()>;
}
```

---

## Phase 4: Developer Experience

### Environment Integration
- [ ] `forks switch alice` - Write .env file with fork URLs
- [ ] `forks env alice` - Print environment variables
- [ ] Shell completion (bash, zsh, fish)

### CI/CD Integration
- [ ] GitHub Action for creating PR preview environments
- [ ] Automatic cleanup on PR close

---

## Phase 5: Advanced Features

### Fork from Snapshot
```bash
forks create -n alice --from production --at "2024-01-15T10:00:00Z"
```

### Fork Sharing
```bash
forks share alice --with bob@example.com
```

### Cost Tracking
```bash
forks cost
# Shows estimated monthly cost per fork
```

---

## Success Metrics

1. **Installation**: `curl | sh` works on Mac/Linux
2. **First fork**: Under 30 seconds from install to working fork
3. **Reliability**: 99%+ success rate for create/delete
4. **Documentation**: Complete guides for all supported providers

---

## Current Status

| Component | Status |
|-----------|--------|
| CLI binary | ✅ Builds and runs |
| Turso integration | ✅ Implemented |
| S3/Tigris integration | ✅ Implemented |
| Config parsing | ✅ Implemented |
| Documentation | ✅ Live at forkstack.xyz |
| End-to-end testing | 🔄 In progress |
| crates.io publish | ⏳ Pending |
| install.sh | ⏳ Pending |
