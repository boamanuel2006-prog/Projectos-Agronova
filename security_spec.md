# AgroNova Firestore Security Specification

## 1. Data Invariants
1. **User Profile Ownership & PII Isolation**: A `/users/{userId}` document may only be read or created by the authenticated, email-verified user whose `request.auth.uid == userId` (or an administrator). Users may never self-assign elevated roles (`ADMIN`).
2. **Listing Integrity**: Every `/listings/{listingId}` document must have `sellerId == request.auth.uid` on creation, non-negative `price` and `quantity`, bounded strings matching `firebase-blueprint.json`, and server timestamps (`request.time`). Once `status == 'ARCHIVED'`, non-admin updates are locked.
3. **Sub-collection Master Gate**: `/users/{userId}/cartItems/{itemId}` and `/users/{userId}/notifications/{notificationId}` require the parent `/users/{userId}` document to exist, `ownerId == request.auth.uid`, and strict field allowlists on updates.
4. **Admin Isolation**: `/admins/{userId}` is read-only (`allow list, write: if false`).

## 2. The "Dirty Dozen" Payloads (All Must Return `PERMISSION_DENIED`)
1. Unauthenticated read of `/users/uid-123` (PII protection).
2. Authenticated user `uid-A` reading `/users/uid-B` (cross-user PII isolation).
3. Authenticated user creating `/users/uid-A` with `role: "ADMIN"` (privilege escalation guard).
4. Authenticated user updating `/users/uid-A` with extra shadow field `isVerified: true` (shadow update guard).
5. Unverified email user (`email_verified == false`) creating a listing or profile (verified-user gate).
6. User creating `/listings/id1` with `sellerId: "other-user"` (identity spoofing).
7. User creating `/listings/id1` with `price: -100` or `title` exceeding 180 chars (boundary guard).
8. User creating `/listings/id1` with client-forged `createdAt` not equal to `request.time` (temporal integrity).
9. Non-owner updating `/listings/id1` owned by another seller (ownership guard).
10. Seller updating an `ARCHIVED` listing (terminal state lock).
11. User querying `/listings` with an unauthenticated request for `DRAFT` status or listing `/users/uid-B/cartItems` (query trust / list enforcement).
12. User creating a document with an invalid 1500-char junk document ID (ID poisoning guard).
