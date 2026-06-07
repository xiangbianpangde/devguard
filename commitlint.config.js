// ============================================================
// commitlint.config.js
// ============================================================
// 03-git §二 落地的可运行配置
// Conventional Commits 提交格式校验（红线 2/3）
// 配套 npm 依赖：npm install --save-dev @commitlint/cli @commitlint/config-conventional
// 配套 husky: npx husky add .husky/commit-msg 'npx --no -- commitlint --edit $1'
// 模板版本：docs/templates/devguard/commitlint.config.js
// ============================================================
module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'type-enum': [
      2,
      'always',
      ['feat', 'fix', 'refactor', 'docs', 'style', 'test', 'chore', 'perf'],
    ],
    'subject-case': [2, 'never', ['upper-case']],
    'subject-min-length': [2, 'always', 5],
    'body-max-line-length': [1, 'always', 100],
  },
};
