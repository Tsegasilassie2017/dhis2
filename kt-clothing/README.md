# KT Clothing

A responsive clothing designer portfolio with an editorial layout, collection filters,
mobile navigation, and a design brief download form. Built with HTML, CSS, and JavaScript.

## Run locally

```sh
python3 -m http.server 8000
```

Open the server in your browser. No build or dependencies required.

## Customize and launch

- Replace the styling inspiration photographs with your own product photography.
- Add real designer contact details to the contact section. The form currently downloads
  a brief locally; it does not send messages or collect customer data.
- Edit collection names and brand copy in `index.html`; colors and layout in `styles.css`.
- Images load from Unsplash and fonts from Google Fonts; system font fallbacks are provided.
- Deploy these three site files with GitHub Pages or any static website host.

The images are explicitly labeled as a visual moodboard and do not represent original KT products.

## Launch readiness

Included: favicon, social-card artwork, page description and Open Graph text,
keyboard skip link, announced collection filters, Escape-to-close mobile menu,
reduced-motion support, and navigation that remains usable without JavaScript.
The privacy note describes the current local-only brief form and external image/font requests.

Still needed from the business: public contact details, designer introduction,
confirmed services and pricing approach, original logo/product photography, and final domain.
Once a domain is selected, add the canonical URL, an absolute Open Graph image URL
(using a PNG/JPEG export of `social-card.svg`), and a sitemap for that domain.
Update the privacy note if enquiry delivery or analytics is added.

### Static hosting

Publish only this `kt-clothing` directory. For Netlify or Vercel, use `kt-clothing`
as the project root/publish directory, no framework and no build command. For GitHub
Pages, use a Pages Actions workflow that uploads only `kt-clothing` as its site artifact;
the branch publishing setting does not offer arbitrary subfolders. Do not publish
DHIS2 data exports or credentials. Publishing requires a separate hosting action.

### Local development in VS Code

Open this folder and use Live Server, or run the Python server above from this folder.
Check the browser console and test phone/desktop widths before each release.

## KT Clothing business details

Designer: Kibretsion Gebrmariam. Focus: women's office dresses, with colors and
styling based on customer preferences. Location: Summit Condominium 2, Addis Ababa.
The map link searches the neighborhood; it is not a verified shop pin.

Add the actual public phone number and full social profile URLs in `business.js`.
Empty or invalid contacts stay hidden. These are public details, never secrets.
Real prices have not yet been provided; the site offers a price-enquiry/quote brief
and does not invent prices, fabric inclusions, or delivery commitments.

## Publish with Yagara hosting

This is a static site; no Node.js, database, PHP, or build step is required.

1. Enable your domain and HTTPS using the hosting account's supported controls.
2. Back up any existing website in the domain's document root before uploading.
3. Upload the **contents** of `kt-clothing` to the document root assigned to your
   domain (often `public_html`; confirm the actual path in your account).
4. Keep `index.html`, `styles.css`, `script.js`, `business.js`, `favicon.svg`, and
   `social-card.svg` together at the same level. Do not upload the whole DHIS2 repo.
5. Open the final HTTPS domain and verify photos, mobile navigation, collection
   filters, brief downloads, phone links, and each social profile on a real phone.
6. Set the canonical URL, social sharing image URL, and sitemap after confirming
   the final domain. Use the same HTTPS address consistently.

The form downloads a brief locally. Yagara hosting alone does not turn it into a
message delivery service. Customers must contact the designer separately.
