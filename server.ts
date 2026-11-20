import express from 'express';
import http from 'http';
import path from 'path';
import crypto from 'crypto';
import { fileURLToPath } from 'url';
import { WebSocketServer, WebSocket } from 'ws';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const PORT = Number(process.env.PORT) || 3000;
const IS_PROD = process.env.NODE_ENV === 'production';

interface UserRecord {
  id: number;
  email: string;
  password: string;
  phone: string | null;
  is_verified: boolean;
  is_staff: boolean;
  date_joined: string;
  profile: {
    full_name: string;
    role: string;
    bio: string;
    photo: string | null;
    verification_status: string;
    city: string;
    province: string;
  };
}

interface CategoryRecord {
  id: number;
  name: string;
  slug: string;
  description: string;
  is_active: boolean;
}

interface ListingRecord {
  id: string;
  seller: number;
  seller_name: string;
  category: CategoryRecord;
  title: string;
  description: string;
  price: number;
  currency: string;
  unit: string;
  quantity: number;
  status: string;
  location_text: string;
  province: string;
  municipality: string;
  images: Array<{ id: number; image: string; sort_order: number }>;
  created_at: string;
  updated_at: string;
}

interface NotificationRecord {
  id: string;
  user_id: number;
  title: string;
  message: string;
  read_at: string | null;
  created_at: string;
}

interface CartItemRecord {
  id: string;
  listing: string;
  quantity: number;
}

// In-memory store (replaces Django PostgreSQL + Redis in AI Studio runtime)
let nextUserId = 3;
let nextListingId = 7;

const users: UserRecord[] = [
  {
    id: 1,
    email: 'admin@agronova.ao',
    password: process.env.DEMO_ADMIN_PASSWORD || 'admin12345',
    phone: '+244923000001',
    is_verified: true,
    is_staff: true,
    date_joined: new Date(Date.now() - 1000 * 60 * 60 * 24 * 25).toISOString(),
    profile: {
      full_name: 'Administrador AgroNova',
      role: 'ADMIN',
      bio: 'Equipa operacional AgroNova',
      photo: null,
      verification_status: 'VERIFIED',
      city: 'Luanda',
      province: 'Luanda',
    },
  },
  {
    id: 2,
    email: 'produtor@agronova.ao',
    password: process.env.DEMO_FARMER_PASSWORD || 'agronova123',
    phone: '+244923000002',
    is_verified: true,
    is_staff: false,
    date_joined: new Date(Date.now() - 1000 * 60 * 60 * 24 * 14).toISOString(),
    profile: {
      full_name: 'Cooperativa Planalto Central',
      role: 'FARMER',
      bio: 'Produção sustentável de grãos e hortícolas no Huambo.',
      photo: null,
      verification_status: 'VERIFIED',
      city: 'Huambo',
      province: 'Huambo',
    },
  },
];

const categories: CategoryRecord[] = [
  { id: 1, name: 'Cereais e Grãos', slug: 'cereais-graos', description: 'Milho, arroz, sorgo e massango.', is_active: true },
  { id: 2, name: 'Leguminosas', slug: 'leguminosas', description: 'Feijão, amendoim e soja.', is_active: true },
  { id: 3, name: 'Hortícolas', slug: 'horticolas', description: 'Tomate, cebola, repolho e pimento.', is_active: true },
  { id: 4, name: 'Raízes e Tubérculos', slug: 'raizes-tuberculos', description: 'Mandioca, batata-rena e batata-doce.', is_active: true },
  { id: 5, name: 'Frutas', slug: 'frutas', description: 'Banana, manga, abacaxi e citrinos.', is_active: true },
  { id: 6, name: 'Café e Cacau', slug: 'cafe-cacau', description: 'Grãos de café arábica, robusta e cacau.', is_active: true },
];

const listings: ListingRecord[] = [
  {
    id: '1',
    seller: 2,
    seller_name: 'Cooperativa Planalto Central',
    category: categories[0],
    title: 'Milho Amarelo Seco',
    description: 'Milho amarelo selecionado da colheita recente no planalto central, ensacado em sacos de 50 kg com baixa humidade.',
    price: 420,
    currency: 'AOA',
    unit: 'kg',
    quantity: 3500,
    status: 'PUBLISHED',
    location_text: 'Bailundo, Huambo',
    province: 'Huambo',
    municipality: 'Bailundo',
    images: [],
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 5).toISOString(),
    updated_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 5).toISOString(),
  },
  {
    id: '2',
    seller: 2,
    seller_name: 'Fazenda Serra da Chela',
    category: categories[1],
    title: 'Feijão Manteiga da Huíla',
    description: 'Feijão manteiga de primeira qualidade, limpo e pronto para escoamento por grosso ou retalho.',
    price: 1150,
    currency: 'AOA',
    unit: 'kg',
    quantity: 1200,
    status: 'PUBLISHED',
    location_text: 'Lubango, Huíla',
    province: 'Huíla',
    municipality: 'Lubango',
    images: [],
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 4).toISOString(),
    updated_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 4).toISOString(),
  },
  {
    id: '3',
    seller: 2,
    seller_name: 'Quinta Vale do Bengo',
    category: categories[2],
    title: 'Tomate Fresco de Mesa',
    description: 'Tomate colhido no ponto ideal de maturação, embalado em caixas ventiladas de 25 kg.',
    price: 18500,
    currency: 'AOA',
    unit: 'caixa',
    quantity: 85,
    status: 'PUBLISHED',
    location_text: 'Caxito, Bengo',
    province: 'Bengo',
    municipality: 'Dande',
    images: [],
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 3).toISOString(),
    updated_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 3).toISOString(),
  },
  {
    id: '4',
    seller: 2,
    seller_name: 'Fazenda Rio Lucala',
    category: categories[3],
    title: 'Mandioca Branca Fresca',
    description: 'Raízes frescas de mandioca doce, ideais para farinha musseque ou consumo direto.',
    price: 280,
    currency: 'AOA',
    unit: 'kg',
    quantity: 4800,
    status: 'PUBLISHED',
    location_text: 'Cacuso, Malanje',
    province: 'Malanje',
    municipality: 'Cacuso',
    images: [],
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 2).toISOString(),
    updated_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 2).toISOString(),
  },
  {
    id: '5',
    seller: 2,
    seller_name: 'Pomares do Kwanza',
    category: categories[4],
    title: 'Banana Pão Selecionada',
    description: 'Cachos selecionados com transporte refrigerado disponível para Luanda e Benguela.',
    price: 650,
    currency: 'AOA',
    unit: 'kg',
    quantity: 2000,
    status: 'PUBLISHED',
    location_text: 'Sumbe, Kwanza Sul',
    province: 'Kwanza Sul',
    municipality: 'Sumbe',
    images: [],
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 1).toISOString(),
    updated_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 1).toISOString(),
  },
  {
    id: '6',
    seller: 2,
    seller_name: 'Produtores do Quitexe',
    category: categories[5],
    title: 'Café Robusta do Uíge',
    description: 'Café robusta seco ao sol, lote de altitude pronto para torrefação ou exportação.',
    price: 2900,
    currency: 'AOA',
    unit: 'kg',
    quantity: 640,
    status: 'PUBLISHED',
    location_text: 'Quitexe, Uíge',
    province: 'Uíge',
    municipality: 'Quitexe',
    images: [],
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 8).toISOString(),
    updated_at: new Date(Date.now() - 1000 * 60 * 60 * 8).toISOString(),
  },
];

const tokens = new Map<string, number>();
const refreshTokens = new Map<string, number>();
const notifications: NotificationRecord[] = [];
const carts = new Map<number, CartItemRecord[]>();
const orders: Array<{ id: string; user_id: number; total: number; status: string; created_at: string }> = [
  { id: 'ord-1001', user_id: 2, total: 84000, status: 'COMPLETED', created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 6).toISOString() },
  { id: 'ord-1002', user_id: 2, total: 55500, status: 'PAID', created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 3).toISOString() },
  { id: 'ord-1003', user_id: 2, total: 115000, status: 'DELIVERED', created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 1).toISOString() },
];
const userSockets = new Map<number, Set<WebSocket>>();

function sanitizeUser(user: UserRecord) {
  return {
    id: user.id,
    email: user.email,
    phone: user.phone,
    is_verified: user.is_verified,
    is_staff: user.is_staff,
    date_joined: user.date_joined,
    profile: user.profile,
  };
}

function issueTokens(userId: number) {
  const access = crypto.randomBytes(24).toString('hex');
  const refresh = crypto.randomBytes(24).toString('hex');
  tokens.set(access, userId);
  refreshTokens.set(refresh, userId);
  return { access, refresh };
}

function getAuthUser(req: express.Request): UserRecord | null {
  const authHeader = req.headers.authorization;
  if (!authHeader?.startsWith('Bearer ')) return null;
  const token = authHeader.slice(7).trim();
  const userId = tokens.get(token);
  if (!userId) return null;
  return users.find((u) => u.id === userId) || null;
}

function pushNotification(userId: number, title: string, message: string) {
  const notif: NotificationRecord = {
    id: crypto.randomUUID(),
    user_id: userId,
    title,
    message,
    read_at: null,
    created_at: new Date().toISOString(),
  };
  notifications.unshift(notif);
  const sockets = userSockets.get(userId);
  if (sockets) {
    const payload = JSON.stringify({ type: 'notification.created', notification: notif });
    for (const ws of sockets) {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(payload);
      }
    }
  }
  return notif;
}

function buildAnalytics(days: number) {
  const safeDays = Math.max(1, Math.min(days || 30, 365));
  const now = new Date();
  const series: Array<{ date: string; users: number; listings: number; orders: number; sales: number; consultations: number }> = [];
  for (let i = safeDays - 1; i >= 0; i--) {
    const d = new Date(now);
    d.setDate(d.getDate() - i);
    const dateStr = d.toISOString().slice(0, 10);
    const dayOrders = orders.filter((o) => o.created_at.slice(0, 10) === dateStr);
    const dayListings = listings.filter((l) => l.created_at.slice(0, 10) === dateStr);
    const dayUsers = users.filter((u) => u.date_joined.slice(0, 10) === dateStr);
    series.push({
      date: dateStr,
      users: dayUsers.length,
      listings: dayListings.length,
      orders: dayOrders.length,
      sales: dayOrders.reduce((acc, o) => acc + o.total, 0),
      consultations: 0,
    });
  }

  const grossSales = orders.reduce((acc, o) => acc + o.total, 0);
  const countBy = <T, K extends string>(items: T[], getKey: (item: T) => K, fieldName: string) => {
    const counts = new Map<string, number>();
    for (const item of items) {
      const k = getKey(item);
      counts.set(k, (counts.get(k) || 0) + 1);
    }
    return Array.from(counts.entries()).map(([k, count]) => ({ [fieldName]: k, count }));
  };

  return {
    summary: {
      period_days: safeDays,
      generated_at: now.toISOString(),
      users: users.length,
      verified_users: users.filter((u) => u.is_verified).length,
      active_users: users.length,
      new_users: users.length,
      listings: listings.length,
      published_listings: listings.filter((l) => l.status === 'PUBLISHED').length,
      new_listings: listings.length,
      orders: orders.length,
      paid_orders: orders.length,
      completed_orders: orders.filter((o) => o.status === 'COMPLETED').length,
      gross_sales: grossSales,
      completed_sales: orders.filter((o) => o.status === 'COMPLETED').reduce((a, o) => a + o.total, 0),
      average_order_value: orders.length ? Math.round(grossSales / orders.length) : 0,
      consultation_requests: 2,
      consultations_completed: 1,
      deliveries: orders.length,
      open_reports: 0,
      average_review: 4.8,
    },
    timeseries: series,
    breakdowns: {
      users_by_role: countBy(users, (u) => u.profile.role, 'role'),
      orders_by_status: countBy(orders, (o) => o.status, 'status'),
      listings_by_status: countBy(listings, (l) => l.status, 'status'),
      consultations_by_status: [{ status: 'COMPLETED', count: 1 }, { status: 'PENDING', count: 1 }],
    },
  };
}

async function startServer() {
  const app = express();
  app.use(express.json());

  app.get('/health/', (_req, res) => {
    res.json({ status: 'ok', service: 'agronova-api' });
  });

  app.get('/readiness/', (_req, res) => {
    res.json({ status: 'ready', checks: { database: 'in-memory', redis: 'in-memory' } });
  });

  // Catalog
  app.get('/api/v1/catalog/categories/', (_req, res) => {
    res.json({ results: categories.filter((c) => c.is_active) });
  });

  // Listings
  app.get('/api/v1/listings/', (req, res) => {
    const user = getAuthUser(req);
    const visible = listings.filter((l) => l.status === 'PUBLISHED' || (user && l.seller === user.id));
    res.json({ results: visible });
  });

  app.post('/api/v1/listings/', (req, res) => {
    const user = getAuthUser(req);
    if (!user) {
      return res.status(401).json({ detail: 'Autenticação necessária.' });
    }
    const { title, description = '', category, price, currency = 'AOA', unit = 'kg', quantity, status = 'DRAFT', location_text = '' } = req.body || {};
    if (!title || price === undefined || quantity === undefined) {
      return res.status(400).json({ detail: 'Preencha título, preço e quantidade.' });
    }
    const cat = categories.find((c) => c.id === Number(category)) || categories[0];
    const now = new Date().toISOString();
    const listing: ListingRecord = {
      id: String(nextListingId++),
      seller: user.id,
      seller_name: user.profile.full_name,
      category: cat,
      title: String(title),
      description: String(description),
      price: Number(price),
      currency: String(currency),
      unit: String(unit),
      quantity: Number(quantity),
      status: String(status),
      location_text: String(location_text),
      province: '',
      municipality: '',
      images: [],
      created_at: now,
      updated_at: now,
    };
    listings.unshift(listing);
    pushNotification(user.id, 'Anúncio criado', `O anúncio "${listing.title}" foi guardado como ${listing.status === 'PUBLISHED' ? 'publicado' : 'rascunho'}.`);
    return res.status(201).json(listing);
  });

  app.post('/api/v1/listings/:id/publish/', (req, res) => {
    const user = getAuthUser(req);
    if (!user) return res.status(401).json({ detail: 'Autenticação necessária.' });
    const listing = listings.find((l) => l.id === req.params.id);
    if (!listing) return res.status(404).json({ detail: 'Anúncio não encontrado.' });
    if (listing.seller !== user.id && !user.is_staff) return res.status(403).json({ detail: 'Sem permissão.' });
    listing.status = 'PUBLISHED';
    listing.updated_at = new Date().toISOString();
    return res.json(listing);
  });

  // Auth
  app.post('/api/v1/auth/register/', (req, res) => {
    const { email, password, phone = null, full_name, role = 'FARMER' } = req.body || {};
    const normalizedEmail = String(email || '').trim().toLowerCase();
    if (!normalizedEmail || !password || String(password).length < 8 || !full_name) {
      return res.status(400).json({ detail: 'Preencha nome, e-mail válido e senha com pelo menos 8 caracteres.' });
    }
    if (users.some((u) => u.email === normalizedEmail)) {
      return res.status(400).json({ detail: 'Já existe uma conta registada com este e-mail.' });
    }
    const user: UserRecord = {
      id: nextUserId++,
      email: normalizedEmail,
      password: String(password),
      phone: phone || null,
      is_verified: false,
      is_staff: false,
      date_joined: new Date().toISOString(),
      profile: {
        full_name: String(full_name),
        role: String(role || 'FARMER'),
        bio: '',
        photo: null,
        verification_status: 'PENDING',
        city: '',
        province: '',
      },
    };
    users.push(user);
    const pair = issueTokens(user.id);
    pushNotification(user.id, 'Bem-vindo ao AgroNova', `Conta criada para ${user.profile.full_name}.`);
    return res.status(201).json({ data: { user: sanitizeUser(user), ...pair } });
  });

  app.post('/api/v1/auth/token/', (req, res) => {
    const { email, password } = req.body || {};
    const normalizedEmail = String(email || '').trim().toLowerCase();
    const user = users.find((u) => u.email === normalizedEmail && u.password === String(password || ''));
    if (!user) {
      return res.status(401).json({ detail: 'E-mail ou senha inválidos.' });
    }
    return res.json(issueTokens(user.id));
  });

  app.post('/api/v1/auth/token/refresh/', (req, res) => {
    const { refresh } = req.body || {};
    const userId = refreshTokens.get(String(refresh || ''));
    if (!userId) return res.status(401).json({ detail: 'Token inválido.' });
    return res.json(issueTokens(userId));
  });

  app.get('/api/v1/auth/me/', (req, res) => {
    const user = getAuthUser(req);
    if (!user) return res.status(401).json({ detail: 'Não autenticado.' });
    return res.json(sanitizeUser(user));
  });

  app.get('/api/v1/auth/profile/', (req, res) => {
    const user = getAuthUser(req);
    if (!user) return res.status(401).json({ detail: 'Não autenticado.' });
    return res.json({ user: sanitizeUser(user), ...user.profile });
  });

  // Notifications
  app.get('/api/v1/notifications/', (req, res) => {
    const user = getAuthUser(req);
    if (!user) return res.status(401).json({ detail: 'Não autenticado.' });
    return res.json({ results: notifications.filter((n) => n.user_id === user.id) });
  });

  app.get('/api/v1/notifications/unread_count/', (req, res) => {
    const user = getAuthUser(req);
    if (!user) return res.status(401).json({ detail: 'Não autenticado.' });
    const count = notifications.filter((n) => n.user_id === user.id && !n.read_at).length;
    return res.json({ count });
  });

  app.post('/api/v1/notifications/read_all/', (req, res) => {
    const user = getAuthUser(req);
    if (!user) return res.status(401).json({ detail: 'Não autenticado.' });
    const now = new Date().toISOString();
    let marked = 0;
    for (const n of notifications) {
      if (n.user_id === user.id && !n.read_at) {
        n.read_at = now;
        marked++;
      }
    }
    return res.json({ marked_read: marked });
  });

  app.post('/api/v1/notifications/:id/read/', (req, res) => {
    const user = getAuthUser(req);
    if (!user) return res.status(401).json({ detail: 'Não autenticado.' });
    const n = notifications.find((x) => x.id === req.params.id && x.user_id === user.id);
    if (!n) return res.status(404).json({ detail: 'Notificação não encontrada.' });
    if (!n.read_at) n.read_at = new Date().toISOString();
    return res.json(n);
  });

  // Cart
  app.get('/api/v1/cart/', (req, res) => {
    const user = getAuthUser(req);
    if (!user) return res.status(401).json({ detail: 'Não autenticado.' });
    return res.json({ items: carts.get(user.id) || [] });
  });

  app.post('/api/v1/cart/items/', (req, res) => {
    const user = getAuthUser(req);
    if (!user) return res.status(401).json({ detail: 'Autenticação necessária.' });
    const { listing: listingId, quantity = 1 } = req.body || {};
    const listing = listings.find((l) => l.id === String(listingId));
    if (!listing) {
      return res.status(400).json({ error: { code: 'CART_INVALID', message: 'Produto não encontrado.' } });
    }
    const items = carts.get(user.id) || [];
    const existing = items.find((i) => i.listing === listing.id);
    if (existing) {
      existing.quantity += Number(quantity) || 1;
      carts.set(user.id, items);
      pushNotification(user.id, 'Carrinho atualizado', `${listing.title} atualizado no carrinho.`);
      return res.status(201).json({ id: existing.id, message: 'Item adicionado ao carrinho.' });
    }
    const item: CartItemRecord = { id: crypto.randomUUID(), listing: listing.id, quantity: Number(quantity) || 1 };
    items.push(item);
    carts.set(user.id, items);
    pushNotification(user.id, 'Produto adicionado ao carrinho', `${listing.title} foi adicionado ao seu carrinho.`);
    return res.status(201).json({ id: item.id, message: 'Item adicionado ao carrinho.' });
  });

  app.post('/api/v1/cart/checkout/', (req, res) => {
    const user = getAuthUser(req);
    if (!user) return res.status(401).json({ detail: 'Autenticação necessária.' });
    const items = carts.get(user.id) || [];
    if (!items.length) {
      return res.status(400).json({ error: { code: 'CHECKOUT_INVALID', message: 'O carrinho está vazio.' } });
    }
    const total = items.reduce((sum, item) => {
      const l = listings.find((x) => x.id === item.listing);
      return sum + (l ? l.price * item.quantity : 0);
    }, 0);
    const orderId = `ord-${1000 + orders.length + 1}`;
    orders.push({ id: orderId, user_id: user.id, total, status: 'PAID', created_at: new Date().toISOString() });
    carts.set(user.id, []);
    pushNotification(user.id, 'Pedido confirmado', `Pedido ${orderId} registado no valor de ${total.toLocaleString('pt-AO')} AOA.`);
    return res.status(201).json({ orders: [orderId], message: 'Checkout concluído; pedidos aguardam confirmação do vendedor.' });
  });

  // Admin analytics
  app.get('/api/v1/admin-analytics/dashboard/', (req, res) => {
    const user = getAuthUser(req);
    if (!user?.is_staff) {
      return res.status(403).json({ detail: 'Acesso restrito a administradores.' });
    }
    const days = Number(req.query.days) || 30;
    return res.json(buildAnalytics(days));
  });

  app.get('/api/v1/admin-analytics/export.csv', (req, res) => {
    const days = Number(req.query.days) || 30;
    const data = buildAnalytics(days);
    res.setHeader('Content-Type', 'text/csv; charset=utf-8');
    res.setHeader('Content-Disposition', 'attachment; filename="agronova-analytics.csv"');
    const header = 'data,novos_utilizadores,novos_anuncios,pedidos,vendas,consultorias';
    const rows = data.timeseries.map((r) => `${r.date},${r.users},${r.listings},${r.orders},${r.sales},${r.consultations}`);
    res.send([header, ...rows].join('\n'));
  });

  // Frontend serving (Vite dev middleware in dev, static dist in prod)
  if (!IS_PROD) {
    const { createServer: createViteServer } = await import('vite');
    const vite = await createViteServer({
      root: path.resolve(__dirname, 'web'),
      server: { middlewareMode: true, hmr: false },
      appType: 'spa',
    });
    app.use(vite.middlewares);
  } else {
    const distDir = path.resolve(__dirname, 'web/dist');
    app.use(express.static(distDir));
    app.get('*', (_req, res) => {
      res.sendFile(path.join(distDir, 'index.html'));
    });
  }

  const httpServer = http.createServer(app);

  // Multiplex WebSocket notifications on port 3000
  const wss = new WebSocketServer({ server: httpServer, path: '/ws/notifications/' });
  wss.on('connection', (ws, req) => {
    const url = new URL(req.url || '/', `http://${req.headers.host || 'localhost'}`);
    const token = url.searchParams.get('token') || '';
    const userId = tokens.get(token);
    if (!userId) {
      ws.close(4001, 'Unauthorized');
      return;
    }
    let set = userSockets.get(userId);
    if (!set) {
      set = new Set();
      userSockets.set(userId, set);
    }
    set.add(ws);
    ws.on('close', () => {
      set?.delete(ws);
    });
  });

  httpServer.listen(PORT, '0.0.0.0', () => {
    console.log(`AgroNova server listening on http://0.0.0.0:${PORT}`);
  });
}

startServer().catch((err) => {
  console.error('Failed to start AgroNova server:', err);
  process.exit(1);
});
