/// <reference types="cypress" />

describe('Responsive Layout Tests', () => {
  beforeEach(() => {
    cy.visit('/')
  })

  const viewports = [
    { width: 320, height: 568, name: 'iPhone SE' },
    { width: 375, height: 812, name: 'iPhone 14' },
    { width: 768, height: 1024, name: 'iPad Mini' },
    { width: 1024, height: 768, name: 'iPad Pro' },
    { width: 1920, height: 1080, name: 'Desktop HD' },
  ]

  viewports.forEach(({ width, height, name }) => {
    it(`renders dashboard correctly at ${name} (${width}x${height})`, () => {
      cy.viewport(width, height)
      cy.wait(500) // Wait for responsive layout to settle

      // Verify header is visible
      cy.contains('Executive Overview').should('be.visible')

      // On mobile (below 768px), bottom nav should be visible
      if (width < 768) {
        cy.get('nav[aria-label="Mobile navigation"]').should('be.visible')
        cy.get('nav[aria-label="Main navigation"]').should('not.be.visible')
      } else {
        cy.get('nav[aria-label="Main navigation"]').should('be.visible')
        cy.get('nav[aria-label="Mobile navigation"]').should('not.exist')
      }

      // Key navigation elements
      cy.get('header').should('be.visible')
      cy.get('main[role="main"]').should('be.visible')

      // Check no horizontal overflow
      cy.document().then((doc) => {
        const body = doc.body
        expect(body.scrollWidth).to.be.at.most(body.clientWidth + 10) // Allow small scrollbar width
      })
    })
  })

  it('navigates to all pages on mobile', () => {
    cy.viewport(375, 812)

    const pages = [
      { label: 'Overview', expected: 'Executive Overview' },
      { label: 'Rankings', expected: 'Candidate Rankings' },
      { label: 'Profile', expected: 'Candidate Details' },
      { label: 'Compare', expected: 'Candidate Comparison' },
      { label: 'Explain', expected: 'AI Explainability' },
      { label: 'Analytics', expected: 'Analytics & Insights' },
      { label: 'Honeypot', expected: 'Honeypot Detection' },
    ]

    pages.forEach((page) => {
      cy.contains('nav[aria-label="Mobile navigation"] button', page.label).click()
      cy.wait(300)
      cy.contains(page.expected).should('be.visible')
    })
  })

  it('renders responsive chart containers', () => {
    // Charts should have min-height set
    cy.get('.recharts-responsive-container').each(($el) => {
      cy.wrap($el).should('be.visible')
      // Check that the parent has a min-height that's responsive
      cy.wrap($el).parent().should('have.css', 'min-height')
    })
  })

  it('shows mobile card mode for rankings table', () => {
    cy.viewport(375, 812)

    // Navigate to rankings
    cy.contains('nav[aria-label="Mobile navigation"] button', 'Rankings').click()
    cy.wait(300)

    // On mobile, should see card mode (div-based, not table)
    cy.get('table').should('not.be.visible')

    // Cards should show candidate info
    cy.contains('CAND_').should('be.visible')    // Expand first card
      cy.contains('button[aria-expanded]', 'CAND_').click()
      cy.contains('Tap to collapse').should('be.visible')
  })

  it('renders search page with filters togglable', () => {
    cy.viewport(1024, 768)

    // Navigate to search (sidebar)
    cy.get('nav[aria-label="Main navigation"]').contains('Search & Discovery').click()
    cy.wait(300)
    cy.contains('Search & Discovery').should('be.visible')

    // Toggle filters
    cy.contains('Filters').click()
    cy.contains('Advanced Filters').should('be.visible')

    // Close filters
    cy.contains('Filters').click()
    cy.contains('Advanced Filters').should('not.exist')
  })

  it('supports dark mode toggle', () => {
    cy.viewport(1440, 900)

    // Click dark mode toggle
    cy.get('button[aria-label*="dark mode"]').click()
    cy.get('html').should('have.class', 'dark')

    // Toggle back
    cy.get('button[aria-label*="light mode"]').click()
    cy.get('html').should('not.have.class', 'dark')
  })
})
