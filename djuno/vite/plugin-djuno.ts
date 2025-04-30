import { Plugin } from 'vite';
import * as path from 'path';
import * as fs from 'fs';
import * as mime from 'mime-types';

export default function djunoPlugin(): Plugin {
  return {
    name: 'vite-plugin-djuno',
    transform(src, id) {
      if (id.endsWith('.dj')) {
        const templateMatch = src.match(/<template>([\s\S]*?)<\/template>/);
        const styleMatch = src.match(/<style scoped>([\s\S]*?)<\/style>/);
        const scriptMatch = src.match(/<script lang="ts">([\s\S]*?)<\/script>/);

        let code = 'export default {';
        if (templateMatch) {
          const templateContent = templateMatch[1].trim().replace(/`/g, '\\`');
          code += `template: \`${templateContent}\`,`;
          const slots = templateMatch[1].match(/<slot\s*(name="([^"]+)")?\s*\/?>/g) || [];
          code += `slots: [${slots.map(s => {
            const nameMatch = s.match(/name="([^"]+)"/);
            return `"${nameMatch ? nameMatch[1] : 'default'}"`;
          }).join(', ')}],`;
        }
        if (styleMatch) {
          const styleContent = styleMatch[1].trim().replace(/`/g, '\\`');
          code += `css: \`${styleContent}\`,`;
        }
        if (scriptMatch) {
          code += scriptMatch[1].trim();
        }
        code += '};';

        return {
          code,
          map: null
        };
      }
    },
    configureServer(server) {
      server.middlewares.use('/static', (req, res, next) => {
        const filePath = path.join(process.cwd(), 'static', req.url || '');
        if (fs.existsSync(filePath)) {
          res.setHeader('Content-Type', mime.lookup(filePath) || 'application/octet-stream');
          fs.createReadStream(filePath).pipe(res);
        } else {
          next();
        }
      });
    }
  };
}
