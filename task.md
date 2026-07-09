# Frontend UI Revamp Task Checklist

## The Goal
Upgrade `leases.html`, `lodges.html`, `rooms.html`, and `tenants.html` to a premium Light Theme featuring glassmorphism, gradient buttons, skeleton loaders, and modern data grids with sticky headers—without modifying `style.css`.

## Why This Matters
- **Perceived Value**: A premium UI significantly improves the user's trust and engagement with the application.
- **Perceived Performance**: Using skeleton loaders gives users immediate visual feedback while waiting for data.
- **Maintainability**: Reusing existing classes (`.glass-panel`, `.fade-in`) enforces a consistent design system without polluting stylesheets.

## The Checklist

### 1. Global Layout & Glassmorphism
- [ ] **Background:** Ensure the main container uses a soft, light background that allows glass panels to stand out.
- [ ] **Glass Panels:** Wrap the primary content areas (forms, tables, dashboards) in containers using the `.glass-panel` class.
- [ ] **Animations:** Apply the `.fade-in` class to primary containers so they elegantly appear on load.

### 2. Modern Data Grids with Sticky Headers
- [ ] **Table Container:** Wrap your data tables in a container with a fixed height and scrollable Y-axis.
- [ ] **Sticky Headers:** Ensure the `<th>` elements remain pinned to the top of the table container while scrolling.
- [ ] **Row Styling:** Ensure table rows have a subtle hover effect to make data easily scannable.

### 3. Gradient Buttons
- [ ] **Primary Actions:** Update all primary action buttons (e.g., "Add Lodge", "Create Lease") to use modern gradient aesthetics.
- [ ] **Interaction States:** Ensure buttons have appropriate hover and active states.

### 4. Skeleton Loaders
- [ ] **Initial DOM State:** Implement skeleton loader elements (e.g., placeholder divs with pulsing animations) directly in the HTML where dynamic data will eventually be injected.
- [ ] **Data Hydration:** Update your JavaScript logic to cleanly remove or hide the skeleton loaders once the actual data is rendered.

## Next Steps
How would you approach structuring the skeleton loaders in the HTML before the data arrives? 
Once you have a plan, start implementing the changes in `mock_frontend/lodges.html` first.
