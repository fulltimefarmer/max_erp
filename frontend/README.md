# Max ERP Frontend

Next.js frontend for Max ERP. See the repository root `README.md` for the full
project overview, technology stack and deployment instructions.

## Stack

- Next.js 15 (App Router) + React 19
- shadcn/ui + Tailwind CSS
- Zustand (client state)
- React Hook Form + Zod (form validation)
- Auth.js v5 (credentials provider -> FastAPI JWT)
- react-dropzone, react-markdown

## Local development

```bash
cp .env.example .env.local
npm install
npm run dev
```

Open http://localhost:3000.

## Scripts

- `npm run dev` - start the dev server
- `npm run build` - production build
- `npm run start` - serve the production build
- `npm run lint` - run ESLint
- `npm run typecheck` - run TypeScript checks
