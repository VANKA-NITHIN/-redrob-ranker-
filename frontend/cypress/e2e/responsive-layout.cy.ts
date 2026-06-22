/// <reference types="cypress" />

describe('Responsive Layout Tests', () => {
  beforeEach(() => {
    cy.visit('/', { timeout: 15000 })
    // Wait for React to hydrate and lazy-loaded components to render
    cy.get('main[role="main"]', { timeout: 10000 }).should('exist')
    cy.wait(1000)
  })

  // Mobile: sidebar wrapped in hidden div, bottom nav visible
  it('renders mobile layout at 375px (iPhone 14)', () => {
    cy.viewport(375, 812)

    // Sidebar exists but is hidden on mobile
    cy.get('aside[aria-label="Main navigation"]').should('exist')
    cy.get('aside[aria-label="Main navigation"]').should('not.be.visible')

    // Bottom mobile nav should be visible
    cy.get('nav[aria-label="Mobile navigation"]').should('exist').and('be.visible')

    // Header and main content should be visible
    cy.get('header').should('be.visible')
    cy.get('main[role="main"]').should('be.visible')
  })

  // Desktop: sidebar fully visible
  it('renders desktop layout at 1440px', () => {
    cy.viewport(1440, 900)

    cy.get('aside[aria-label="Main navigation"]').should('exist').and('be.visible')
    cy.get('header').should('be.visible')
    cy.get('main[role="main"]').should('be.visible')
  })

  // Tablet: sidebar visible (may be collapsed)
  it('renders tablet layout at 768px', () => {
    cy.viewport(768, 1024)

    cy.get('aside[aria-label="Main navigation"]').should('exist').and('be.visible')
    cy.get('main[role="main"]').should('be.visible')
  })

  // Navigation
  it('navigates between pages via sidebar on desktop', () => {
    cy.viewport(1440, 900)

    cy.get('aside[aria-label="Main navigation"] button[aria-label="Candidate Rankings"]').click()
    cy.wait(500)
    cy.contains('Candidate Rankings').should('be.visible')

    cy.get('aside[aria-label="Main navigation"] button[aria-label="Analytics"]').click()
    cy.wait(500)
    cy.contains('Analytics & Insights').should('be.visible')
  })

  it('navigates between pages via bottom nav on mobile', () => {
    cy.viewport(375, 812)

    cy.get('nav[aria-label="Mobile navigation"]').contains('Rankings').click()
    cy.wait(500)
    cy.contains('Candidate Rankings').should('be.visible')

    cy.get('nav[aria-label="Mobile navigation"]').contains('Analytics').click()
    cy.wait(500)
    cy.contains('Analytics & Insights').should('be.visible')
  })

  // Rankings table: desktop shows table, mobile shows card mode
  it('shows table on desktop and card mode on mobile', () => {
    // Desktop: table should be visible
    cy.viewport(1440, 900)
    cy.get('aside[aria-label="Main navigation"] button[aria-label="Candidate Rankings"]').click()
    cy.contains('Candidate Rankings', { timeout: 8000 }).should('be.visible')
    cy.wait(500)
    cy.get('table', { timeout: 5000 }).should('exist').and('be.visible')

    // Mobile: table hidden (display:none), cards visible
    cy.viewport(375, 812)
    cy.wait(500)
    cy.get('table', { timeout: 5000 }).should('exist').and('not.be.visible')
    cy.contains('CAND_').should('exist')
  })

  // Dark mode toggle
  it('toggles dark mode', () => {
    cy.viewport(1440, 900)

    // Toggle on
    cy.get('button[aria-label*="dark mode"]').click()
    cy.get('html').should('have.class', 'dark')

    // Toggle off
    cy.get('button[aria-label*="light mode"]').click()
    cy.get('html').should('not.have.class', 'dark')
  })

  // No horizontal overflow on any viewport
  it('has no horizontal overflow at any common viewport', () => {
    const sizes = [
      { w: 320, h: 568 },
      { w: 375, h: 812 },
      { w: 768, h: 1024 },
      { w: 1024, h: 768 },
      { w: 1440, h: 900 },
      { w: 1920, h: 1080 },
    ]

    sizes.forEach(({ w, h }) => {
      cy.viewport(w, h)
      cy.wait(300)
      cy.document().then((doc) => {
        const body = doc.body
        const overflow = body.scrollWidth - body.clientWidth
        expect(overflow, `Overflow at ${w}x${h}: ${overflow}px`).to.be.at.most(20)
      })
    })
  })
})
