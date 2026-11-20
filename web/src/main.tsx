import React, { useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import {
  User,
  onAuthStateChanged,
  signInWithPopup,
  signOut,
} from 'firebase/auth';
import {
  collection,
  deleteDoc,
  doc,
  getDoc,
  onSnapshot,
  query,
  serverTimestamp,
  setDoc,
  updateDoc,
  where,
  writeBatch,
} from 'firebase/firestore';
import './styles.css';
import { request } from './auth/api';
import {
  auth,
  db,
  googleProvider,
  handleFirestoreError,
  OperationType,
} from './firebase';
import { ErrorBoundary } from './components/ErrorBoundary';

type Listing = {
  id: string;
  sellerId?: string;
  seller_name?: string;
  title: string;
  description?: string;
  price: string | number;
  currency?: string;
  unit?: string;
  quantity?: string | number;
  status?: string;
  category?: any;
  location_text?: string;
  createdAtMs?: number;
  source?: 'firestore' | 'catalog';
};

type Category = {
  id: number;
  name: string;
  slug: string;
};

type UserProfileData = {
  uid: string;
  displayName: string;
  email: string;
  photoURL: string | null;
  role: 'FARMER' | 'BUYER' | 'COMPANY' | 'TRANSPORTER' | 'CONSULTANT';
  preferredCategory: string;
};

type CartItemData = {
  id: string;
  ownerId: string;
  listingId: string;
  title: string;
  price: number;
  currency: string;
  unit: string;
  quantity: number;
};

type FavoriteData = {
  id: string;
  ownerId: string;
  listingId: string;
  title: string;
};

type OrderData = {
  id: string;
  ownerId: string;
  deliveryAddress: string;
  paymentMethod: 'MULTICAIXA_EXPRESS' | 'BANK_TRANSFER' | 'CASH_ON_DELIVERY';
  itemsSummary: string;
  itemsCount: number;
  total: number;
  currency: string;
  status: 'CONFIRMED' | 'PREPARING' | 'DELIVERED' | 'CANCELLED';
  createdAt: any;
};

type NotificationData = {
  id: string;
  ownerId: string;
  title: string;
  message: string;
  readAt: any;
  createdAt: any;
};

const HERO_IMAGE = '/src/assets/images/hero_agronova_harvest_1795103406776.jpg';

const CATEGORY_IMAGES: Record<string, string> = {
  '1': '/src/assets/images/cat_cereais_milho_1795103406444.jpg',
  'cereais-graos': '/src/assets/images/cat_cereais_milho_1795103406444.jpg',
  '2': '/src/assets/images/cat_leguminosas_feijao_1795103406756.jpg',
  'leguminosas': '/src/assets/images/cat_leguminosas_feijao_1795103406756.jpg',
  '3': '/src/assets/images/cat_horticolas_tomate_1795103406917.jpg',
  'horticolas': '/src/assets/images/cat_horticolas_tomate_1795103406917.jpg',
  '4': '/src/assets/images/cat_tuberculos_mandioca_1795103406523.jpg',
  'raizes-tuberculos': '/src/assets/images/cat_tuberculos_mandioca_1795103406523.jpg',
  '5': '/src/assets/images/cat_frutas_banana_1795103407013.jpg',
  'frutas': '/src/assets/images/cat_frutas_banana_1795103407013.jpg',
  '6': '/src/assets/images/cat_cafe_robusta_1795103406946.jpg',
  'cafe-cacau': '/src/assets/images/cat_cafe_robusta_1795103406946.jpg',
};

const SAFE_ID_REGEX = /^[a-zA-Z0-9_-]+$/;
const ALLOWED_CURRENCIES = ['AOA', 'USD', 'EUR'] as const;
const ALLOWED_ROLES = ['FARMER', 'BUYER', 'COMPANY', 'TRANSPORTER', 'CONSULTANT'] as const;

const ORDER_STATUS_LABEL: Record<string, string> = {
  CONFIRMED: 'Confirmado',
  PREPARING: 'Em preparação',
  DELIVERED: 'Entregue',
  CANCELLED: 'Cancelado',
};

const PAYMENT_LABELS: Record<string, string> = {
  MULTICAIXA_EXPRESS: 'Multicaixa Express',
  BANK_TRANSFER: 'Transferência Bancária',
  CASH_ON_DELIVERY: 'Pagamento na Entrega',
};

function getListingImage(listing: Listing): string {
  const catId = listing.category?.id !== undefined ? String(listing.category.id) : '';
  const catSlug = String(listing.category?.slug || '');
  return CATEGORY_IMAGES[catSlug] || CATEGORY_IMAGES[catId] || CATEGORY_IMAGES['1'];
}

function sanitizeText(value: string, maxLen: number): string {
  return value.trim().slice(0, maxLen);
}

function makeSafeId(prefix: string): string {
  const raw = `${prefix}-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
  return raw.replace(/[^a-zA-Z0-9_-]/g, '').slice(0, 128);
}

function HeartIcon({ filled }: { filled: boolean }) {
  return (
    <svg width="17" height="17" viewBox="0 0 24 24" fill={filled ? 'currentColor' : 'none'} stroke="currentColor" strokeWidth="2" aria-hidden="true">
      <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" />
    </svg>
  );
}

function App() {
  const [firebaseUser, setFirebaseUser] = useState<User | null>(null);
  const [authReady, setAuthReady] = useState(false);
  const [userProfile, setUserProfile] = useState<UserProfileData | null>(null);
  const [authModal, setAuthModal] = useState<'login' | 'profile' | null>(null);
  const [authBusy, setAuthBusy] = useState(false);
  const [authError, setAuthError] = useState('');

  const [seedListings, setSeedListings] = useState<Listing[]>([]);
  const [publishedFsListings, setPublishedFsListings] = useState<Listing[]>([]);
  const [ownFsListings, setOwnFsListings] = useState<Listing[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);

  const [q, setQ] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'recent' | 'price-asc' | 'price-desc' | 'stock-desc'>('recent');
  const [onlyFavorites, setOnlyFavorites] = useState(false);

  const [selected, setSelected] = useState<Listing | null>(null);
  const [pdpQty, setPdpQty] = useState(1);
  const [creating, setCreating] = useState(false);

  const [cartItems, setCartItems] = useState<CartItemData[]>([]);
  const [favorites, setFavorites] = useState<FavoriteData[]>([]);
  const [orders, setOrders] = useState<OrderData[]>([]);
  const [notifications, setNotifications] = useState<NotificationData[]>([]);

  const [showCart, setShowCart] = useState(false);
  const [showOrders, setShowOrders] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const [toast, setToast] = useState<string>('');
  const [heroImgFailed, setHeroImgFailed] = useState(false);
  const [failedImages, setFailedImages] = useState<Record<string, boolean>>({});

  function showToast(msg: string) {
    setToast(msg);
    window.setTimeout(() => {
      setToast((prev) => (prev === msg ? '' : prev));
    }, 3500);
  }

  useEffect(() => {
    Promise.all([request('/listings/'), request('/catalog/categories/')])
      .then(([a, c]) => {
        const list = (a.data ?? a.results ?? a ?? []).map((item: Listing, idx: number) => ({
          ...item,
          id: String(item.id),
          createdAtMs: Date.now() - idx * 3600000,
          source: 'catalog' as const,
        }));
        setSeedListings(list);
        setCategories(c.data ?? c.results ?? c ?? []);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (user) => {
      setFirebaseUser(user);
      setAuthReady(true);

      if (!user) {
        setUserProfile(null);
        setPublishedFsListings([]);
        setOwnFsListings([]);
        setCartItems([]);
        setFavorites([]);
        setOrders([]);
        setNotifications([]);
        setOnlyFavorites(false);
        return;
      }

      const userPath = `users/${user.uid}`;
      try {
        const userRef = doc(db, 'users', user.uid);
        const snap = await getDoc(userRef);
        if (!snap.exists()) {
          const safeName =
            sanitizeText(user.displayName || user.email?.split('@')[0] || 'Utilizador AgroNova', 120) ||
            'Utilizador AgroNova';
          const safeEmail = sanitizeText(user.email || '', 160);
          const safePhoto = user.photoURL ? sanitizeText(user.photoURL, 500) : null;
          await setDoc(userRef, {
            uid: user.uid,
            displayName: safeName,
            email: safeEmail,
            photoURL: safePhoto,
            role: 'FARMER',
            preferredCategory: 'all',
            createdAt: serverTimestamp(),
            updatedAt: serverTimestamp(),
          });
        }
      } catch (error) {
        handleFirestoreError(error, OperationType.WRITE, userPath);
      }
    });

    return () => unsubscribe();
  }, []);

  useEffect(() => {
    if (!authReady || !firebaseUser) return;
    const uid = firebaseUser.uid;

    const userUnsub = onSnapshot(
      doc(db, 'users', uid),
      (snap) => {
        if (snap.exists()) {
          setUserProfile(snap.data() as UserProfileData);
        }
      },
      (error) => handleFirestoreError(error, OperationType.GET, `users/${uid}`)
    );

    const mapListingDoc = (d: any): Listing => {
      const data = d.data();
      return {
        id: d.id,
        sellerId: data.sellerId,
        seller_name: data.sellerName,
        title: data.title,
        description: data.description,
        price: data.price,
        currency: data.currency,
        unit: data.unit,
        quantity: data.quantity,
        status: data.status,
        location_text: data.locationText,
        createdAtMs: data.createdAt?.toMillis?.() ?? Date.now(),
        category: {
          id: data.categoryId,
          name: data.categoryName,
          slug: data.categorySlug,
        },
        source: 'firestore',
      };
    };

    const publishedUnsub = onSnapshot(
      query(collection(db, 'listings'), where('status', '==', 'PUBLISHED')),
      (snapshot) => setPublishedFsListings(snapshot.docs.map(mapListingDoc)),
      (error) => handleFirestoreError(error, OperationType.LIST, 'listings')
    );

    const ownUnsub = onSnapshot(
      query(collection(db, 'listings'), where('sellerId', '==', uid)),
      (snapshot) => setOwnFsListings(snapshot.docs.map(mapListingDoc)),
      (error) => handleFirestoreError(error, OperationType.LIST, 'listings')
    );

    const cartUnsub = onSnapshot(
      query(collection(db, 'users', uid, 'cartItems'), where('ownerId', '==', uid)),
      (snapshot) => {
        setCartItems(
          snapshot.docs.map((d) => ({
            id: d.id,
            ...(d.data() as Omit<CartItemData, 'id'>),
          }))
        );
      },
      (error) => handleFirestoreError(error, OperationType.LIST, `users/${uid}/cartItems`)
    );

    const favUnsub = onSnapshot(
      query(collection(db, 'users', uid, 'favorites'), where('ownerId', '==', uid)),
      (snapshot) => {
        setFavorites(
          snapshot.docs.map((d) => ({
            id: d.id,
            ...(d.data() as Omit<FavoriteData, 'id'>),
          }))
        );
      },
      (error) => handleFirestoreError(error, OperationType.LIST, `users/${uid}/favorites`)
    );

    const ordersUnsub = onSnapshot(
      query(collection(db, 'users', uid, 'orders'), where('ownerId', '==', uid)),
      (snapshot) => {
        const items = snapshot.docs.map((d) => ({
          id: d.id,
          ...(d.data() as Omit<OrderData, 'id'>),
        }));
        items.sort((a, b) => (b.createdAt?.toMillis?.() ?? 0) - (a.createdAt?.toMillis?.() ?? 0));
        setOrders(items);
      },
      (error) => handleFirestoreError(error, OperationType.LIST, `users/${uid}/orders`)
    );

    const notifUnsub = onSnapshot(
      query(collection(db, 'users', uid, 'notifications'), where('ownerId', '==', uid)),
      (snapshot) => {
        const items = snapshot.docs.map((d) => ({
          id: d.id,
          ...(d.data() as Omit<NotificationData, 'id'>),
        }));
        items.sort((a, b) => (b.createdAt?.toMillis?.() ?? 0) - (a.createdAt?.toMillis?.() ?? 0));
        setNotifications(items.slice(0, 30));
      },
      (error) => handleFirestoreError(error, OperationType.LIST, `users/${uid}/notifications`)
    );

    return () => {
      userUnsub();
      publishedUnsub();
      ownUnsub();
      cartUnsub();
      favUnsub();
      ordersUnsub();
      notifUnsub();
    };
  }, [authReady, firebaseUser]);

  const favoriteIds = useMemo(() => new Set(favorites.map((f) => f.listingId)), [favorites]);

  const listings = useMemo(() => {
    const byId = new Map<string, Listing>();
    for (const item of ownFsListings) byId.set(item.id, item);
    for (const item of publishedFsListings) {
      if (!byId.has(item.id)) byId.set(item.id, item);
    }
    for (const item of seedListings) {
      if (!byId.has(item.id)) byId.set(item.id, item);
    }
    return Array.from(byId.values());
  }, [ownFsListings, publishedFsListings, seedListings]);

  const filtered = useMemo(() => {
    const queryLower = q.trim().toLowerCase();
    const list = listings.filter((x) => {
      const catId = x.category?.id !== undefined ? String(x.category.id) : '';
      const catSlug = String(x.category?.slug || '');
      const catName = String(x.category?.name || x.category || '');

      const matchesCategory =
        selectedCategory === 'all' ||
        catId === selectedCategory ||
        catSlug === selectedCategory ||
        catName.toLowerCase() === selectedCategory.toLowerCase();

      if (!matchesCategory) return false;
      if (onlyFavorites && !favoriteIds.has(x.id)) return false;
      if (!queryLower) return true;

      return `${x.title} ${catName} ${x.location_text || ''} ${x.seller_name || ''}`
        .toLowerCase()
        .includes(queryLower);
    });

    if (sortBy === 'price-asc') {
      return [...list].sort((a, b) => Number(a.price) - Number(b.price));
    }
    if (sortBy === 'price-desc') {
      return [...list].sort((a, b) => Number(b.price) - Number(a.price));
    }
    if (sortBy === 'stock-desc') {
      return [...list].sort((a, b) => Number(b.quantity || 0) - Number(a.quantity || 0));
    }
    return [...list].sort((a, b) => (b.createdAtMs || 0) - (a.createdAtMs || 0));
  }, [listings, q, selectedCategory, sortBy, onlyFavorites, favoriteIds]);

  async function handleSelectCategory(categoryKey: string) {
    setSelectedCategory(categoryKey);
    if (firebaseUser) {
      try {
        await updateDoc(doc(db, 'users', firebaseUser.uid), {
          preferredCategory: sanitizeText(categoryKey, 64) || 'all',
          updatedAt: serverTimestamp(),
        });
      } catch (error) {
        handleFirestoreError(error, OperationType.UPDATE, `users/${firebaseUser.uid}`);
      }
    }
  }

  async function handleGoogleSignIn() {
    setAuthBusy(true);
    setAuthError('');
    try {
      await signInWithPopup(auth, googleProvider);
      setAuthModal(null);
      showToast('Sessão iniciada com Google.');
    } catch (error: any) {
      setAuthError(error?.message || 'Não foi possível iniciar sessão com Google.');
    } finally {
      setAuthBusy(false);
    }
  }

  async function handleSignOut() {
    try {
      await signOut(auth);
      setAuthModal(null);
      setShowCart(false);
      setShowOrders(false);
      setShowNotifications(false);
      showToast('Sessão terminada.');
    } catch (error: any) {
      showToast(error?.message || 'Erro ao terminar sessão.');
    }
  }

  async function createNotification(uid: string, title: string, message: string) {
    const notifId = makeSafeId('notif');
    try {
      await setDoc(doc(db, 'users', uid, 'notifications', notifId), {
        ownerId: uid,
        title: sanitizeText(title, 180) || 'Notificação',
        message: sanitizeText(message, 500) || 'Atualização na conta.',
        readAt: null,
        createdAt: serverTimestamp(),
      });
    } catch (error) {
      handleFirestoreError(error, OperationType.CREATE, `users/${uid}/notifications/${notifId}`);
    }
  }

  async function toggleFavorite(listing: Listing, e?: React.MouseEvent) {
    if (e) e.stopPropagation();
    if (!firebaseUser) {
      setAuthModal('login');
      showToast('Entre com Google para guardar produtos favoritos.');
      return;
    }
    const uid = firebaseUser.uid;
    const safeListingId = SAFE_ID_REGEX.test(listing.id) ? listing.id.slice(0, 128) : makeSafeId('fav');
    const favRef = doc(db, 'users', uid, 'favorites', safeListingId);
    const path = `users/${uid}/favorites/${safeListingId}`;
    try {
      if (favoriteIds.has(safeListingId)) {
        await deleteDoc(favRef);
        showToast('Removido dos favoritos.');
      } else {
        await setDoc(favRef, {
          ownerId: uid,
          listingId: safeListingId,
          title: sanitizeText(listing.title, 180) || 'Produto',
          createdAt: serverTimestamp(),
        });
        showToast('Guardado nos favoritos.');
      }
    } catch (error) {
      handleFirestoreError(error, OperationType.WRITE, path);
    }
  }

  async function createListing(payload: {
    title: string;
    description: string;
    category: number;
    price: string;
    currency: string;
    unit: string;
    quantity: string;
    status: 'PUBLISHED' | 'DRAFT';
    location_text: string;
  }) {
    if (!firebaseUser) {
      setAuthModal('login');
      return;
    }

    const cat =
      categories.find((c) => c.id === Number(payload.category)) ||
      categories[0] || { id: 1, name: 'Cereais e Grãos', slug: 'cereais-graos' };

    const listingId = makeSafeId('lst');
    const safePrice = Math.max(0, Number(payload.price) || 0);
    const safeQuantity = Math.max(0, Number(payload.quantity) || 0);
    const safeCurrency = ALLOWED_CURRENCIES.includes(payload.currency as any) ? payload.currency : 'AOA';
    const safeStatus = payload.status === 'DRAFT' ? 'DRAFT' : 'PUBLISHED';
    const safeSellerName =
      sanitizeText(userProfile?.displayName || firebaseUser.displayName || 'Produtor AgroNova', 120) ||
      'Produtor AgroNova';
    const safeTitle = sanitizeText(payload.title, 180);

    try {
      await setDoc(doc(db, 'listings', listingId), {
        sellerId: firebaseUser.uid,
        sellerName: safeSellerName,
        categoryId: Number(cat.id) || 1,
        categoryName: sanitizeText(cat.name, 100) || 'Agricultura',
        categorySlug:
          sanitizeText(cat.slug, 120).toLowerCase().replace(/[^a-z0-9-]/g, '') || 'agricultura',
        title: safeTitle,
        description: sanitizeText(payload.description || '', 2000),
        price: safePrice,
        currency: safeCurrency,
        unit: sanitizeText(payload.unit || 'kg', 40) || 'kg',
        quantity: safeQuantity,
        status: safeStatus,
        locationText: sanitizeText(payload.location_text || 'Angola', 255),
        createdAt: serverTimestamp(),
        updatedAt: serverTimestamp(),
      });

      await createNotification(
        firebaseUser.uid,
        'Anúncio guardado',
        `O produto "${safeTitle}" foi guardado (${safeStatus === 'PUBLISHED' ? 'Publicado' : 'Rascunho'}).`
      );
      setCreating(false);
      showToast('Anúncio publicado com sucesso.');
    } catch (error) {
      handleFirestoreError(error, OperationType.CREATE, `listings/${listingId}`);
    }
  }

  async function toggleListingStatus(listing: Listing) {
    if (!firebaseUser || listing.source !== 'firestore' || listing.sellerId !== firebaseUser.uid) return;
    const nextStatus = listing.status === 'PUBLISHED' ? 'PAUSED' : 'PUBLISHED';
    try {
      await updateDoc(doc(db, 'listings', listing.id), {
        status: nextStatus,
        updatedAt: serverTimestamp(),
      });
      setSelected((prev) => (prev ? { ...prev, status: nextStatus } : null));
      showToast(nextStatus === 'PUBLISHED' ? 'Anúncio publicado.' : 'Anúncio pausado.');
    } catch (error) {
      handleFirestoreError(error, OperationType.UPDATE, `listings/${listing.id}`);
    }
  }

  async function deleteOwnListing(listing: Listing) {
    if (!firebaseUser || listing.source !== 'firestore' || listing.sellerId !== firebaseUser.uid) return;
    try {
      await deleteDoc(doc(db, 'listings', listing.id));
      setSelected(null);
      showToast('Anúncio removido.');
    } catch (error) {
      handleFirestoreError(error, OperationType.DELETE, `listings/${listing.id}`);
    }
  }

  async function addToCart(listing: Listing, qtyToAdd = 1) {
    if (!firebaseUser) {
      setSelected(null);
      setAuthModal('login');
      showToast('Entre com Google para adicionar produtos ao carrinho.');
      return;
    }

    const uid = firebaseUser.uid;
    const safeListingId = SAFE_ID_REGEX.test(listing.id) ? listing.id.slice(0, 128) : makeSafeId('item');
    const itemPath = `users/${uid}/cartItems/${safeListingId}`;
    const amount = Math.max(1, Math.round(qtyToAdd));

    try {
      const existingItem = cartItems.find((i) => i.listingId === safeListingId);
      const itemRef = doc(db, 'users', uid, 'cartItems', safeListingId);

      if (existingItem) {
        await updateDoc(itemRef, {
          quantity: existingItem.quantity + amount,
          updatedAt: serverTimestamp(),
        });
      } else {
        await setDoc(itemRef, {
          ownerId: uid,
          listingId: safeListingId,
          title: sanitizeText(listing.title, 180) || 'Produto',
          price: Math.max(0, Number(listing.price) || 0),
          currency: ALLOWED_CURRENCIES.includes((listing.currency || 'AOA') as any)
            ? listing.currency || 'AOA'
            : 'AOA',
          unit: sanitizeText(listing.unit || 'kg', 40) || 'kg',
          quantity: amount,
          createdAt: serverTimestamp(),
          updatedAt: serverTimestamp(),
        });
      }

      await createNotification(uid, 'Carrinho atualizado', `"${listing.title}" adicionado (${amount}).`);
      setSelected(null);
      setShowCart(true);
      showToast('Produto adicionado ao carrinho.');
    } catch (error) {
      handleFirestoreError(error, OperationType.WRITE, itemPath);
    }
  }

  async function updateCartQuantity(item: CartItemData, delta: number) {
    if (!firebaseUser) return;
    const uid = firebaseUser.uid;
    const nextQty = item.quantity + delta;
    if (nextQty <= 0) {
      await removeFromCart(item.id);
      return;
    }
    try {
      await updateDoc(doc(db, 'users', uid, 'cartItems', item.id), {
        quantity: nextQty,
        updatedAt: serverTimestamp(),
      });
    } catch (error) {
      handleFirestoreError(error, OperationType.UPDATE, `users/${uid}/cartItems/${item.id}`);
    }
  }

  async function removeFromCart(itemId: string) {
    if (!firebaseUser) return;
    const uid = firebaseUser.uid;
    try {
      await deleteDoc(doc(db, 'users', uid, 'cartItems', itemId));
      showToast('Produto removido do carrinho.');
    } catch (error) {
      handleFirestoreError(error, OperationType.DELETE, `users/${uid}/cartItems/${itemId}`);
    }
  }

  async function completeCheckout(deliveryAddress: string, paymentMethod: OrderData['paymentMethod']) {
    if (!firebaseUser || !cartItems.length) return;
    const uid = firebaseUser.uid;
    const safeAddress = sanitizeText(deliveryAddress, 255);
    if (safeAddress.length < 3) {
      showToast('Indique uma morada de entrega válida.');
      return;
    }

    const total = cartItems.reduce((sum, item) => sum + item.price * item.quantity, 0);
    const itemsCount = cartItems.reduce((sum, item) => sum + item.quantity, 0);
    const itemsSummary = sanitizeText(
      cartItems.map((i) => `${i.quantity}x ${i.title}`).join(', '),
      1000
    );

    const orderId = makeSafeId('ord');
    const batch = writeBatch(db);
    batch.set(doc(db, 'users', uid, 'orders', orderId), {
      ownerId: uid,
      deliveryAddress: safeAddress,
      paymentMethod,
      itemsSummary,
      itemsCount,
      total,
      currency: 'AOA',
      status: 'CONFIRMED',
      createdAt: serverTimestamp(),
      updatedAt: serverTimestamp(),
    });
    for (const item of cartItems) {
      batch.delete(doc(db, 'users', uid, 'cartItems', item.id));
    }

    try {
      await batch.commit();
      await createNotification(
        uid,
        'Pedido confirmado',
        `Pedido ${orderId} confirmado (${total.toLocaleString('pt-AO')} AOA).`
      );
      setShowCart(false);
      setShowOrders(true);
      showToast('Pedido confirmado e registado!');
    } catch (error) {
      handleFirestoreError(error, OperationType.WRITE, `users/${uid}/orders/${orderId}`);
    }
  }

  async function cancelOrder(order: OrderData) {
    if (!firebaseUser || order.status !== 'CONFIRMED') return;
    const uid = firebaseUser.uid;
    try {
      await updateDoc(doc(db, 'users', uid, 'orders', order.id), {
        status: 'CANCELLED',
        updatedAt: serverTimestamp(),
      });
      showToast('Pedido cancelado.');
    } catch (error) {
      handleFirestoreError(error, OperationType.UPDATE, `users/${uid}/orders/${order.id}`);
    }
  }

  async function markAllNotificationsRead() {
    if (!firebaseUser) return;
    const uid = firebaseUser.uid;
    const unread = notifications.filter((n) => !n.readAt);
    if (!unread.length) return;
    const batch = writeBatch(db);
    for (const n of unread) {
      batch.update(doc(db, 'users', uid, 'notifications', n.id), {
        readAt: serverTimestamp(),
      });
    }
    try {
      await batch.commit();
    } catch (error) {
      handleFirestoreError(error, OperationType.UPDATE, `users/${uid}/notifications`);
    }
  }

  const unreadCount = notifications.filter((n) => !n.readAt).length;
  const cartCount = cartItems.reduce((sum, item) => sum + item.quantity, 0);

  return (
    <div>
      {/* 3-Zone Top Bar */}
      <header className="topbar">
        <a href="#top" className="brand">
          AgroNova
        </a>

        <nav className="navMenu" aria-label="Navegação principal">
          <a href="#ofertas" className="navLink">
            Marketplace
          </a>
          <button
            type="button"
            className={`navLink ${onlyFavorites ? 'active' : ''}`}
            onClick={() => {
              if (!firebaseUser) {
                setAuthModal('login');
                showToast('Entre com Google para ver os seus favoritos.');
                return;
              }
              setOnlyFavorites((v) => !v);
              document.getElementById('ofertas')?.scrollIntoView({ behavior: 'smooth' });
            }}
          >
            Favoritos
          </button>
          <button
            type="button"
            className="navLink"
            onClick={() => {
              if (!firebaseUser) {
                setAuthModal('login');
                showToast('Entre com Google para acompanhar os seus pedidos.');
                return;
              }
              setShowOrders(true);
            }}
          >
            Meus Pedidos
          </button>
          <button
            type="button"
            className="navLink"
            onClick={() => (firebaseUser ? setCreating(true) : setAuthModal('login'))}
          >
            Vender
          </button>
        </nav>

        <div className="navActions">
          {firebaseUser && (
            <button
              type="button"
              className="iconBtn tabular"
              onClick={() => setShowCart(true)}
            >
              Carrinho ({cartCount})
            </button>
          )}
          <button
            type="button"
            className="iconBtn tabular"
            onClick={() => setShowNotifications((v) => !v)}
            aria-label="Notificações"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
              <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
              <path d="M13.73 21a2 2 0 0 1-3.46 0" />
            </svg>
            <span>{unreadCount}</span>
          </button>
          {firebaseUser ? (
            <>
              <button
                type="button"
                className="ghostBtn profileBtn"
                onClick={() => setAuthModal('profile')}
              >
                {userProfile?.displayName || firebaseUser.displayName || firebaseUser.email}
              </button>
              <button type="button" className="primaryBtn" onClick={handleSignOut}>
                Sair
              </button>
            </>
          ) : (
            <button type="button" className="primaryBtn" onClick={() => setAuthModal('login')}>
              Entrar
            </button>
          )}
        </div>
      </header>

      <main id="top">
        <section className="hero">
          <div className="heroCopy">
            <span className="kicker">Mercado agrícola direto de Angola</span>
            <h1>
              Do campo para o mercado, <em>sem complicação.</em>
            </h1>
            <p className="heroLead">
              Explore colheitas frescas diretamente de cooperativas e produtores nacionais, compare
              preços por unidade e feche pedidos com acompanhamento transparente.
            </p>

            <div className="searchBar">
              <span className="searchIcon" aria-hidden="true">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="11" cy="11" r="8" />
                  <path d="m21 21-4.3-4.3" />
                </svg>
              </span>
              <input
                value={q}
                onChange={(e) => setQ(e.target.value)}
                placeholder="Pesquisar milho, feijão, tomate, Huambo..."
                aria-label="Pesquisar produtos"
              />
              <button
                type="button"
                className="primaryBtn"
                onClick={() => document.getElementById('ofertas')?.scrollIntoView({ behavior: 'smooth' })}
              >
                Pesquisar
              </button>
            </div>

            <div className="heroMetrics tabular">
              <div className="heroMetric">
                <strong>{categories.length || 6} categorias</strong>
                <span>Grãos, hortícolas e frutas</span>
              </div>
              <div className="heroMetric">
                <strong>{listings.length} ofertas</strong>
                <span>Stock ativo no mercado</span>
              </div>
              <div className="heroMetric">
                <strong>Direto</strong>
                <span>Sem intermediários</span>
              </div>
            </div>
          </div>

          <div className="heroMedia">
            {!heroImgFailed ? (
              <img
                src={HERO_IMAGE}
                alt="Colheita fresca de produtores agrícolas angolanos"
                referrerPolicy="no-referrer"
                onError={() => setHeroImgFailed(true)}
              />
            ) : (
              <div className="cardFallback">Produção agrícola de Angola</div>
            )}
            <div className="heroScrim">
              <strong>Colheita certificada das províncias</strong>
              <span>Huambo · Huíla · Bengo · Malanje · Uíge · Kwanza Sul</span>
            </div>
          </div>
        </section>

        <section className="section" id="ofertas">
          <div className="sectionHead">
            <div>
              <span className="kicker">Catálogo</span>
              <h2>Produtos em destaque</h2>
            </div>
            {firebaseUser ? (
              <button type="button" className="primaryBtn" onClick={() => setCreating(true)}>
                + Publicar produto
              </button>
            ) : (
              <button type="button" className="primaryBtn" onClick={() => setAuthModal('login')}>
                Entrar com Google para vender
              </button>
            )}
          </div>

          {/* Barra de filtros por categoria (estado local) + ordenação e favoritos */}
          <div className="toolbar">
            <div className="filterBar" role="tablist" aria-label="Filtrar produtos por categoria">
              <button
                type="button"
                role="tab"
                aria-selected={selectedCategory === 'all'}
                className={`filterBtn ${selectedCategory === 'all' ? 'active' : ''}`}
                onClick={() => handleSelectCategory('all')}
              >
                Todas
              </button>
              {categories.map((cat) => {
                const catKey = String(cat.id);
                const isActive = selectedCategory === catKey;
                return (
                  <button
                    key={cat.id}
                    type="button"
                    role="tab"
                    aria-selected={isActive}
                    className={`filterBtn ${isActive ? 'active' : ''}`}
                    onClick={() => handleSelectCategory(catKey)}
                  >
                    {cat.name}
                  </button>
                );
              })}
            </div>

            <div className="toolbarControls">
              {firebaseUser && (
                <button
                  type="button"
                  className={`filterBtn ${onlyFavorites ? 'active' : ''}`}
                  onClick={() => setOnlyFavorites((v) => !v)}
                >
                  Favoritos ({favorites.length})
                </button>
              )}
              <select
                className="sortSelect"
                aria-label="Ordenar produtos"
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as any)}
              >
                <option value="recent">Mais recentes</option>
                <option value="price-asc">Menor preço</option>
                <option value="price-desc">Maior preço</option>
                <option value="stock-desc">Maior quantidade</option>
              </select>
              <span className="filterMeta tabular">
                {filtered.length} {filtered.length === 1 ? 'produto' : 'produtos'}
              </span>
            </div>
          </div>

          {loading ? (
            <div className="notice">A carregar produtos do marketplace...</div>
          ) : (
            <div className="grid">
              {filtered.length ? (
                filtered.map((x) => {
                  const isFav = favoriteIds.has(x.id);
                  const imgSrc = getListingImage(x);
                  return (
                    <article
                      className="card"
                      key={x.id}
                      onClick={() => {
                        setPdpQty(1);
                        setSelected(x);
                      }}
                    >
                      <div className="cardMedia">
                        {!failedImages[x.id] ? (
                          <img
                            src={imgSrc}
                            alt={x.title}
                            referrerPolicy="no-referrer"
                            onError={() =>
                              setFailedImages((prev) => ({ ...prev, [x.id]: true }))
                            }
                          />
                        ) : (
                          <div className="cardFallback">{x.category?.name || 'Agricultura'}</div>
                        )}
                        <button
                          type="button"
                          className={`favBtn ${isFav ? 'active' : ''}`}
                          aria-label={isFav ? 'Remover dos favoritos' : 'Guardar nos favoritos'}
                          onClick={(e) => toggleFavorite(x, e)}
                        >
                          <HeartIcon filled={isFav} />
                        </button>
                      </div>

                      <div className="cardBody">
                        <div className="cardMeta">
                          {x.category?.name || x.category || 'Agricultura'}
                          {x.location_text ? ` · ${x.location_text}` : ''}
                          {x.status === 'DRAFT' ? ' · Rascunho' : ''}
                          {x.status === 'PAUSED' ? ' · Pausado' : ''}
                        </div>
                        <h3 className="cardTitle">{x.title}</h3>
                        <p className="cardSub tabular">
                          {x.seller_name || 'Produtor nacional'} · {x.quantity ?? '—'} {x.unit || 'un.'}
                        </p>
                        <div className="cardFooter">
                          <div className="cardPrice tabular">
                            {Number(x.price).toLocaleString('pt-AO')} {x.currency || 'AOA'}{' '}
                            <span>/ {x.unit || 'un.'}</span>
                          </div>
                          <button
                            type="button"
                            className="quickAddBtn"
                            onClick={(e) => {
                              e.stopPropagation();
                              addToCart(x, 1);
                            }}
                          >
                            + Carrinho
                          </button>
                        </div>
                      </div>
                    </article>
                  );
                })
              ) : (
                <div className="notice">
                  Nenhum produto corresponde aos filtros atuais.{' '}
                  <button
                    type="button"
                    className="linkBtn"
                    style={{ marginLeft: 8 }}
                    onClick={() => {
                      handleSelectCategory('all');
                      setQ('');
                      setOnlyFavorites(false);
                    }}
                  >
                    Limpar filtros
                  </button>
                </div>
              )}
            </div>
          )}
        </section>

        <section className="steps" aria-label="Como funciona">
          <div className="stepCard">
            <span className="stepNum">01. Pesquisar</span>
            <h3>Encontre por categoria</h3>
            <p>
              Filtre produtos frescos por categoria, província ou ordenação de preço e guarde os
              seus favoritos.
            </p>
          </div>
          <div className="stepCard">
            <span className="stepNum">02. Encomendar</span>
            <h3>Carrinho transparente</h3>
            <p>
              Adicione quantidades por quilo, caixa ou tonelada e escolha o método de pagamento mais
              conveniente.
            </p>
          </div>
          <div className="stepCard">
            <span className="stepNum">03. Acompanhar</span>
            <h3>Histórico de pedidos</h3>
            <p>
              Consulte todos os seus pedidos confirmados e o estado de preparação diretamente na sua
              conta.
            </p>
          </div>
        </section>
      </main>

      <footer>
        <span>AgroNova · Marketplace agrícola de Angola</span>
        <span>Ligando produtores locais a compradores em todo o país</span>
      </footer>

      {showNotifications && (
        <div className="notificationPanel">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
            <h3 style={{ margin: 0 }}>Notificações</h3>
            {firebaseUser && (
              <button type="button" className="ghostBtn" onClick={markAllNotificationsRead}>
                Marcar lidas
              </button>
            )}
          </div>
          {notifications.length ? (
            notifications.map((n) => (
              <div className="notificationItem" key={n.id}>
                <strong>{n.title}</strong>
                <div style={{ color: '#5e685f', marginTop: 2 }}>{n.message}</div>
                <small style={{ color: '#7a837a' }}>
                  {n.createdAt?.toDate ? n.createdAt.toDate().toLocaleString('pt-PT') : 'Agora'}
                </small>
              </div>
            ))
          ) : (
            <p style={{ color: '#5e685f', fontSize: 14 }}>
              {firebaseUser
                ? 'Sem notificações no momento.'
                : 'Entre com Google para acompanhar as notificações da sua conta.'}
            </p>
          )}
        </div>
      )}

      {showCart && firebaseUser && (
        <CartDrawer
          items={cartItems}
          onClose={() => setShowCart(false)}
          onStep={updateCartQuantity}
          onRemove={removeFromCart}
          onCheckout={completeCheckout}
        />
      )}

      {showOrders && firebaseUser && (
        <div className="modal">
          <div className="modalBox modalWide">
            <button type="button" className="close" onClick={() => setShowOrders(false)}>
              ×
            </button>
            <span className="kicker">Histórico</span>
            <h2 style={{ fontFamily: 'var(--font-display)', margin: '8px 0 18px' }}>
              Meus Pedidos
            </h2>
            {orders.length ? (
              orders.map((ord) => (
                <div className="orderCard" key={ord.id}>
                  <div className="orderHeader">
                    <strong className="tabular">Pedido #{ord.id.slice(-8)}</strong>
                    <span className="orderStatus">{ORDER_STATUS_LABEL[ord.status] || ord.status}</span>
                  </div>
                  <div className="orderMeta">
                    <div>Produtos: {ord.itemsSummary}</div>
                    <div>Entrega: {ord.deliveryAddress} · {PAYMENT_LABELS[ord.paymentMethod] || ord.paymentMethod}</div>
                    <div className="tabular" style={{ marginTop: 6, color: 'var(--ink)', fontWeight: 700 }}>
                      Total: {Number(ord.total).toLocaleString('pt-AO')} {ord.currency} ({ord.itemsCount} un.)
                    </div>
                  </div>
                  {ord.status === 'CONFIRMED' && (
                    <button
                      type="button"
                      className="cartRemove"
                      style={{ marginTop: 8, paddingLeft: 0 }}
                      onClick={() => cancelOrder(ord)}
                    >
                      Cancelar pedido
                    </button>
                  )}
                </div>
              ))
            ) : (
              <p style={{ color: 'var(--ink-muted)' }}>Ainda não registou nenhum pedido.</p>
            )}
          </div>
        </div>
      )}

      {selected && (
        <div className="modal">
          <div className="modalBox modalWide">
            <button type="button" className="close" onClick={() => setSelected(null)}>
              ×
            </button>
            <div className="pdpLayout">
              <div className="pdpMedia">
                <img
                  src={getListingImage(selected)}
                  alt={selected.title}
                  referrerPolicy="no-referrer"
                />
              </div>
              <div className="pdpInfo">
                <div className="cardMeta">
                  {selected.category?.name || selected.category || 'Agricultura'}
                  {selected.location_text ? ` · ${selected.location_text}` : ''}
                </div>
                <h2>{selected.title}</h2>
                <p className="pdpDesc">
                  {selected.description || 'Produto agrícola disponível para encomenda direta no AgroNova.'}
                </p>
                <div className="pdpPrice tabular">
                  {Number(selected.price).toLocaleString('pt-AO')} {selected.currency || 'AOA'}{' '}
                  <span style={{ fontSize: 14, fontWeight: 500, color: 'var(--ink-muted)' }}>
                    / {selected.unit || 'un.'}
                  </span>
                </div>
                <div className="pdpMetaRow tabular">
                  Produtor: {selected.seller_name || 'Produtor AgroNova'} · Stock:{' '}
                  {selected.quantity ?? '—'} {selected.unit || 'un.'}
                </div>

                <div className="pdpActions">
                  <div className="stepper">
                    <button
                      type="button"
                      aria-label="Diminuir quantidade"
                      onClick={() => setPdpQty((q) => Math.max(1, q - 1))}
                    >
                      −
                    </button>
                    <span className="tabular">{pdpQty}</span>
                    <button
                      type="button"
                      aria-label="Aumentar quantidade"
                      onClick={() => setPdpQty((q) => q + 1)}
                    >
                      +
                    </button>
                  </div>
                  <button
                    type="button"
                    className="primaryBtn"
                    onClick={() => addToCart(selected, pdpQty)}
                  >
                    Adicionar ao carrinho
                  </button>
                  <button
                    type="button"
                    className="ghostBtn"
                    onClick={() => toggleFavorite(selected)}
                  >
                    <HeartIcon filled={favoriteIds.has(selected.id)} />
                    <span>{favoriteIds.has(selected.id) ? 'Nos favoritos' : 'Favorito'}</span>
                  </button>
                </div>

                {firebaseUser &&
                  selected.source === 'firestore' &&
                  selected.sellerId === firebaseUser.uid && (
                    <div className="sellerBox">
                      <button
                        type="button"
                        className="ghostBtn"
                        onClick={() => toggleListingStatus(selected)}
                      >
                        {selected.status === 'PUBLISHED' ? 'Pausar anúncio' : 'Publicar anúncio'}
                      </button>
                      <button
                        type="button"
                        className="cartRemove"
                        onClick={() => deleteOwnListing(selected)}
                      >
                        Eliminar anúncio
                      </button>
                    </div>
                  )}
              </div>
            </div>
          </div>
        </div>
      )}

      {creating && firebaseUser && (
        <CreateListing
          categories={categories}
          onClose={() => setCreating(false)}
          onCreate={createListing}
        />
      )}

      {authModal === 'login' && (
        <div className="modal">
          <div className="modalBox">
            <button type="button" className="close" onClick={() => setAuthModal(null)}>
              ×
            </button>
            <span className="kicker">Acesso seguro</span>
            <h2 style={{ fontFamily: 'var(--font-display)', margin: '8px 0 12px' }}>
              Entrar no AgroNova
            </h2>
            <p style={{ color: 'var(--ink-muted)', lineHeight: 1.6 }}>
              Inicie sessão com a sua conta Google para publicar produtos, guardar favoritos, gerir o
              carrinho e acompanhar pedidos.
            </p>
            <button
              type="button"
              className="googleBtn"
              disabled={authBusy}
              onClick={handleGoogleSignIn}
            >
              <svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true">
                <path
                  fill="#4285F4"
                  d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v4.51h6.6c-.29 1.52-1.14 2.82-2.4 3.68v3.05h3.88c2.27-2.09 3.665-5.17 3.665-9.17Z"
                />
                <path
                  fill="#34A853"
                  d="M12 24c3.3 0 6.08-1.09 8.11-2.96l-3.88-3.05c-1.09.73-2.49 1.16-4.23 1.16-3.26 0-6.02-2.2-7-5.16H1.01v3.14C3.05 21.2 7.24 24 12 24Z"
                />
                <path
                  fill="#FBBC05"
                  d="M5 13.99c-.25-.73-.39-1.52-.39-2.33s.14-1.6.39-2.33V6.19H1.01C.37 7.46 0 8.89 0 11.66s.37 4.2 1.01 5.47l3.99-3.14Z"
                />
                <path
                  fill="#EA4335"
                  d="M12 4.75c1.8 0 3.41.62 4.68 1.84l3.51-3.51C18.08 1.19 15.3 0 12 0 7.24 0 3.05 2.8 1.01 6.86l3.99 3.14c.98-2.96 3.74-5.25 7-5.25Z"
                />
              </svg>
              {authBusy ? 'A autenticar...' : 'Continuar com Google'}
            </button>
            {authError && <p className="error">{authError}</p>}
          </div>
        </div>
      )}

      {authModal === 'profile' && firebaseUser && (
        <Profile
          user={firebaseUser}
          profile={userProfile}
          onClose={() => setAuthModal(null)}
          onUpdated={() => showToast('Perfil atualizado.')}
        />
      )}

      {toast && <div className="toast">{toast}</div>}
    </div>
  );
}

function CartDrawer({
  items,
  onClose,
  onStep,
  onRemove,
  onCheckout,
}: {
  items: CartItemData[];
  onClose: () => void;
  onStep: (item: CartItemData, delta: number) => void;
  onRemove: (itemId: string) => void;
  onCheckout: (address: string, paymentMethod: OrderData['paymentMethod']) => Promise<void>;
}) {
  const [address, setAddress] = useState('');
  const [payment, setPayment] = useState<OrderData['paymentMethod']>('MULTICAIXA_EXPRESS');
  const [submitting, setSubmitting] = useState(false);

  const total = items.reduce((sum, item) => sum + item.price * item.quantity, 0);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    try {
      await onCheckout(address, payment);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="drawerBackdrop" onClick={onClose}>
      <div className="drawer" onClick={(e) => e.stopPropagation()}>
        <button type="button" className="close" onClick={onClose}>
          ×
        </button>
        <span className="kicker">Encomenda</span>
        <h2>Carrinho</h2>

        {items.length ? (
          <>
            <div style={{ flex: 1 }}>
              {items.map((item) => (
                <div className="cartRow" key={item.id}>
                  <div>
                    <strong style={{ fontSize: 15 }}>{item.title}</strong>
                    <div className="tabular" style={{ fontSize: 13, color: 'var(--ink-muted)', marginTop: 4 }}>
                      {item.price.toLocaleString('pt-AO')} {item.currency} / {item.unit}
                    </div>
                    <button
                      type="button"
                      className="cartRemove"
                      style={{ paddingLeft: 0, marginTop: 4 }}
                      onClick={() => onRemove(item.id)}
                    >
                      Remover
                    </button>
                  </div>
                  <div className="stepper">
                    <button type="button" onClick={() => onStep(item, -1)}>
                      −
                    </button>
                    <span className="tabular">{item.quantity}</span>
                    <button type="button" onClick={() => onStep(item, 1)}>
                      +
                    </button>
                  </div>
                </div>
              ))}
            </div>

            <form className="checkoutBox" onSubmit={handleSubmit}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 12 }}>
                <span style={{ color: 'var(--ink-muted)' }}>Subtotal</span>
                <strong className="tabular" style={{ fontSize: 18 }}>
                  {total.toLocaleString('pt-AO')} AOA
                </strong>
              </div>
              <label>
                Local de entrega (Município / Província)
                <input
                  value={address}
                  onChange={(e) => setAddress(e.target.value)}
                  placeholder="Ex.: Talatona, Luanda"
                  minLength={3}
                  maxLength={255}
                  required
                />
              </label>
              <label>
                Método de pagamento
                <select
                  value={payment}
                  onChange={(e) => setPayment(e.target.value as OrderData['paymentMethod'])}
                >
                  <option value="MULTICAIXA_EXPRESS">Multicaixa Express</option>
                  <option value="BANK_TRANSFER">Transferência Bancária</option>
                  <option value="CASH_ON_DELIVERY">Pagamento na Entrega</option>
                </select>
              </label>
              <button type="submit" className="primaryBtn wide" disabled={submitting}>
                {submitting ? 'A confirmar...' : 'Confirmar pedido'}
              </button>
            </form>
          </>
        ) : (
          <p style={{ color: 'var(--ink-muted)' }}>O seu carrinho está vazio.</p>
        )}
      </div>
    </div>
  );
}

function Profile({
  user,
  profile,
  onClose,
  onUpdated,
}: {
  user: User;
  profile: UserProfileData | null;
  onClose: () => void;
  onUpdated: () => void;
}) {
  const [displayName, setDisplayName] = useState(profile?.displayName || user.displayName || '');
  const [saving, setSaving] = useState(false);

  async function saveProfile(e: React.FormEvent) {
    e.preventDefault();
    const safeName = sanitizeText(displayName, 120);
    if (!safeName) return;
    setSaving(true);
    try {
      await updateDoc(doc(db, 'users', user.uid), {
        displayName: safeName,
        updatedAt: serverTimestamp(),
      });
      onUpdated();
      onClose();
    } catch (error) {
      handleFirestoreError(error, OperationType.UPDATE, `users/${user.uid}`);
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="modal">
      <div className="modalBox">
        <button type="button" className="close" onClick={onClose}>
          ×
        </button>
        <span className="kicker">Minha conta</span>
        <h2 style={{ fontFamily: 'var(--font-display)', margin: '8px 0 8px' }}>
          {profile?.displayName || user.displayName || user.email}
        </h2>
        <p style={{ color: 'var(--ink-muted)', margin: '0 0 8px' }}>{user.email}</p>
        <p style={{ color: 'var(--ink-muted)', margin: '0 0 16px', fontSize: 13 }}>
          Perfil:{' '}
          <b>
            {ALLOWED_ROLES.includes((profile?.role || 'FARMER') as any)
              ? profile?.role || 'FARMER'
              : 'FARMER'}
          </b>
        </p>
        <form onSubmit={saveProfile}>
          <label>
            Nome de exibição
            <input
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              maxLength={120}
              required
            />
          </label>
          <button className="primaryBtn wide" type="submit" disabled={saving}>
            {saving ? 'A guardar...' : 'Guardar perfil'}
          </button>
        </form>
      </div>
    </div>
  );
}

function CreateListing({
  categories,
  onClose,
  onCreate,
}: {
  categories: Category[];
  onClose: () => void;
  onCreate: (p: {
    title: string;
    description: string;
    category: number;
    price: string;
    currency: string;
    unit: string;
    quantity: string;
    status: 'PUBLISHED' | 'DRAFT';
    location_text: string;
  }) => Promise<void>;
}) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState(categories[0]?.id?.toString() || '1');
  const [price, setPrice] = useState('');
  const [unit, setUnit] = useState('kg');
  const [quantity, setQuantity] = useState('');
  const [location, setLocation] = useState('');
  const [status, setStatus] = useState<'PUBLISHED' | 'DRAFT'>('PUBLISHED');
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError('');
    try {
      await onCreate({
        title,
        description,
        category: Number(category),
        price,
        currency: 'AOA',
        unit,
        quantity,
        status,
        location_text: location,
      });
    } catch (e: any) {
      setError(e.message || 'Erro ao guardar anúncio.');
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="modal">
      <div className="modalBox">
        <button type="button" className="close" onClick={onClose}>
          ×
        </button>
        <span className="kicker">Novo anúncio</span>
        <h2 style={{ fontFamily: 'var(--font-display)', margin: '8px 0 14px' }}>
          Publicar produto
        </h2>
        <form onSubmit={submit}>
          <label>
            Nome do produto
            <input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Ex.: Milho amarelo"
              maxLength={180}
              required
            />
          </label>
          <label>
            Categoria
            <select value={category} onChange={(e) => setCategory(e.target.value)} required>
              {categories.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
          </label>
          <div className="formGrid">
            <label>
              Preço (AOA)
              <input
                type="number"
                min="0"
                step="0.01"
                value={price}
                onChange={(e) => setPrice(e.target.value)}
                required
              />
            </label>
            <label>
              Unidade
              <select value={unit} onChange={(e) => setUnit(e.target.value)}>
                <option>kg</option>
                <option>tonelada</option>
                <option>caixa</option>
                <option>litro</option>
                <option>unidade</option>
              </select>
            </label>
          </div>
          <div className="formGrid">
            <label>
              Quantidade
              <input
                type="number"
                min="0"
                step="0.001"
                value={quantity}
                onChange={(e) => setQuantity(e.target.value)}
                required
              />
            </label>
            <label>
              Estado
              <select
                value={status}
                onChange={(e) => setStatus(e.target.value as 'PUBLISHED' | 'DRAFT')}
              >
                <option value="PUBLISHED">Publicar imediatamente</option>
                <option value="DRAFT">Guardar como rascunho</option>
              </select>
            </label>
          </div>
          <label>
            Localização
            <input
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              placeholder="Município, província"
              maxLength={255}
            />
          </label>
          <label>
            Descrição
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
              maxLength={2000}
              placeholder="Qualidade, colheita, disponibilidade..."
            />
          </label>
          <button className="primaryBtn wide" disabled={saving}>
            {saving ? 'A guardar...' : 'Guardar anúncio'}
          </button>
          {error && <p className="error">{error}</p>}
        </form>
      </div>
    </div>
  );
}

createRoot(document.getElementById('root')!).render(
  <ErrorBoundary>
    <App />
  </ErrorBoundary>
);
