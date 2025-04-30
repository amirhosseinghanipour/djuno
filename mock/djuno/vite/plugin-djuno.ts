import { Plugin } from 'vite';
import * as path from 'path';
import * as fs from 'fs';
import * as mime from 'mime-types';

export default function djunoPlugin(): Plugin {
  return {
    name: 'vite-plugin-djuno',
    transform(src, id) {
      if (id.endsWith('.dj')) {
        const templateMatch = src.match(/<template>(.*?)<\/template>/s);
        const styleMatch = src.match(/<style scoped>(.*?)<\/style>/s);
        const scriptMatch = src.match(/<script lang="ts">(.*?)<\/script>/s);
        
        let code = 'export default {';
        if (templateMatch) {
          code += `template: \`${templateMatch[1].trim()}\`,`;
          const slots = templateMatch[1].match(/<slot\s*(name="([^"]+)")?\s*\/?>/g) || [];
          code += `slots: [${slots.map(s => {
            const nameMatch = s.match(/name="([^"]+)"/);
            return `"${nameMatch ? nameMatch[1] : 'default'}"`;
          }).join(', ')}],`;
        }
        if (styleMatch) {
          code += `css: \`${styleMatch[1].trim()}\`,`;
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
        const filePath = path.join(process.cwd(), 'static', req.url);
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
