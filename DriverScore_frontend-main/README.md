# Driver Score frontend

Driver Score Analytics Dasboard.

## Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type aware lint rules:

-   Configure the top-level `parserOptions` property like this:

```js
export default {
    // other rules...
    parserOptions: {
        ecmaVersion: "latest",
        sourceType: "module",
        project: ["./tsconfig.json", "./tsconfig.node.json"],
        tsconfigRootDir: __dirname,
    },
};
```

-   Replace `plugin:@typescript-eslint/recommended` to `plugin:@typescript-eslint/recommended-type-checked` or `plugin:@typescript-eslint/strict-type-checked`
-   Optionally add `plugin:@typescript-eslint/stylistic-type-checked`
-   Install [eslint-plugin-react](https://github.com/jsx-eslint/eslint-plugin-react) and add `plugin:react/recommended` & `plugin:react/jsx-runtime` to the `extends` list

-   Within the `frontend` directory, install the necessary NPM packages:

```bash
npm install
```

-   And start the live server with the following `npm` script:

```bash
npm run dev
```

-   Then open your browser at http://localhost:5173/.

## Generate Client

-   Start the Docker Compose stack.

-   Download the OpenAPI JSON file from `http://localhost/api/v1/openapi.json` and copy it to a new file `openapi.json` at the root of the `frontend` directory.

-   To simplify the names in the generated frontend client code, modify the `openapi.json` file by running the following script:

```bash
node modify-openapi-operationids.js
```

-   To generate the frontend client, run:

```bash
npm run generate-client
```

-   Commit the changes.

Notice that everytime the backend changes (changing the OpenAPI schema), you should follow these steps again to update the frontend client.

## Using a Remote API

If you want to use a remote API, you can set the environment variable `VITE_API_URL` to the URL of the remote API. For example, you can set it in the `frontend/.env` file:

```env
VITE_API_URL=https://my-remote-api.example.com
```

Then, when you run the frontend, it will use that URL as the base URL for the API.

## Code Structure

The frontend code is structured as follows:

-   `frontend/src` - The main frontend code.
-   `frontend/src/assets` - Static assets.
-   `frontend/src/client` - The generated OpenAPI client.
-   `frontend/src/components` - The different components of the frontend.
-   `frontend/src/hooks` - Custom hooks.
-   `frontend/src/routes` - The different routes of the frontend which include the pages.
-   `theme.tsx` - The Chakra UI custom theme.

## TODO:

-   Fix gradient bar
-   Short time of cache to avoid clogging the memory
-   Fly to map while waiting for IMU data
-   React memo to seperate the cursor and the heavy map
-   Throttle (doesn't work)
