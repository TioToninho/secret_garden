# Secret Garden Frontend

Frontend para o sistema de gestão imobiliária Secret Garden.

## Estrutura do Projeto

```
src/
├── assets/           # Recursos estáticos (imagens, fontes, etc)
├── components/       # Componentes reutilizáveis
│   ├── common/      # Componentes genéricos (botões, inputs, etc)
│   ├── layout/      # Componentes de layout (header, footer, etc)
│   └── property/    # Componentes específicos de imóveis
├── config/          # Configurações do projeto
├── hooks/           # Custom hooks React
├── pages/           # Páginas/rotas da aplicação
│   ├── admin/       # Páginas administrativas
│   ├── auth/        # Páginas de autenticação
│   └── public/      # Páginas públicas
├── services/        # Serviços e integrações com API
│   ├── api/         # Configuração e métodos da API
│   └── storage/     # Serviços de armazenamento local
├── store/           # Gerenciamento de estado (Redux/Context)
├── styles/          # Arquivos de estilo globais
├── types/           # Definições de tipos TypeScript
└── utils/           # Funções utilitárias

```

## Tecnologias Principais

- React
- TypeScript
- Vite
- TailwindCSS
- React Router
- Axios
- React Query

## Scripts Disponíveis

- `npm run dev`: Inicia o servidor de desenvolvimento
- `npm run build`: Gera a build de produção
- `npm run preview`: Visualiza a build de produção localmente
- `npm run lint`: Executa o linter
- `npm run test`: Executa os testes 