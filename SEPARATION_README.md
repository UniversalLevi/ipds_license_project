
# 📂 Project Folder Structure (Agent & Client Separation - Server as Agent)

This project has been split into two logical parts (where **Agent = Server-side** and **Client = Endpoint-side user machine**):

---

## ✅ agent/ (Server-side components: API, database, key generation)

| Folder/File | Purpose |
|---|---|
| api/ | FastAPI-based server (license generation, verification API endpoints) |
| db/ | Database seed scripts |
| rsa/ | RSA key generation scripts for license signing |
| scripts/ | Server-side setup scripts (like database initialization) |
| database.sql | Database schema |
| PROJECT_STRUCTURE.md | Project structure documentation |
| README.md | General project overview |
| SECURITY_OVERVIEW.md | Security design documentation |
| readme.txt | Additional readme info |

---

## ✅ client/ (Client-side agent: runs on end-user machine)

| Folder/File | Purpose |
|---|---|
| agent/ | CLI tool and supporting utilities for license fetching and saving |
| verifier/ | License verification tool (used on the client machine for checking validity) |
| license_info.json | Holds local license info for the agent |

---

## ✅ Summary:

- **Agent Folder** → Everything the **server/API** runs.
- **Client Folder** → Everything the **client/agent system** runs on the **user/endpoint machines** (that contacts the server and verifies licenses locally).
