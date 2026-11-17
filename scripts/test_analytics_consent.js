#!/usr/bin/env node
'use strict';
// Consent regression suite. No external packages or network; simulates DOM events.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');

const root = path.resolve(__dirname, '..');
const html = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
const trust = fs.readFileSync(path.join(root, 'gdpr-ai-trust.html'), 'utf8');
const oldLoader = '<script async src="https://www.googletagmanager.com/gtag/js?id=';
assert(!html.includes(oldLoader), 'Unconditional Google Analytics loader is still present');
assert(html.includes('cookie-consent[hidden]'), 'Consent dialog should be hidden when dismissed');
assert(html.includes('id="analyticsPreferences"'), 'Cookie preferences must reopen');
assert(html.includes('href="forrasok/"'), 'Authority directory link missing');
assert(html.includes('data-news-grid'), 'Member press section was accidentally removed');
assert(html.includes('id="media-okoszisztema"'), 'Media publications overview missing');
assert(trust.includes('Opcionális látogatottságmérés'), 'Privacy disclosure missing');

const block = html.match(/<script>\s*\/\* Basic Consent Mode v2:([\s\S]*?)<\/script>/);
assert(block, 'Consent-only script missing');
const script = '/* Basic Consent Mode v2:' + block[1];

function scenario(choice) {
  const storage = new Map();
  if (choice != null) storage.set('ks-analytics-consent-v1', choice);
  const events = {};
  const elements = {};
  for (const id of ['analyticsConsent','analyticsPreferences','analyticsAccept','analyticsReject']) {
    elements[id] = {
      hidden: true,
      focus() {},
      addEventListener(type, listener) { events[id + ':' + type] = listener; },
    };
  }
  const scripts = [];
  let reloads = 0;
  const pageWindow = {location:{reload(){reloads += 1;}}};
  const pageDocument = {
    getElementById(id) {return elements[id] || null;},
    createElement(tag) {
      assert.equal(tag, 'script');
      return {src:'',async:false};
    },
    head:{
      appendChild(node){
        scripts.push(node.src);
        return node;
      },
    },
  };
  const sandbox = {
    window:pageWindow,
    document:pageDocument,
    Date,
    encodeURIComponent,
    localStorage:{
      getItem(key){return storage.has(key)?storage.get(key):null;},
      setItem(key,value){storage.set(key,value);}
    }
  };
  vm.runInNewContext(script, sandbox, {timeout:1000});
  return {storage,events,elements,scripts,pageWindow,get reloads(){return reloads;}};
}

const fresh = scenario(null);
assert.equal(fresh.scripts.length, 0, 'Tracking loaded before initial consent');
assert.equal(fresh.elements.analyticsConsent.hidden, false, 'Initial choice must be presented');
fresh.events['analyticsReject:click']();
assert.equal(fresh.storage.get('ks-analytics-consent-v1'), 'denied');
assert.equal(fresh.scripts.length, 0, 'Tracking loaded after rejection');
assert.equal(fresh.pageWindow['ga-disable-G-1FC22JEX2F'], true);
fresh.events['analyticsPreferences:click']();
assert.equal(fresh.elements.analyticsConsent.hidden, false, 'Preferences cannot reopen');

const accepted = scenario(null);
accepted.events['analyticsAccept:click']();
assert.equal(accepted.scripts.length,1, 'Analytics must load exactly once after consent');
assert(accepted.scripts[0].includes('https://www.googletagmanager.com/gtag/js?id=G-1FC22JEX2F'));
assert.equal(accepted.storage.get('ks-analytics-consent-v1'), 'granted');
assert.equal(accepted.pageWindow['ga-disable-G-1FC22JEX2F'],false);
assert.equal(accepted.pageWindow.dataLayer.length,4);
assert.equal(accepted.pageWindow.dataLayer[0][0], 'consent');
assert.equal(accepted.pageWindow.dataLayer[0][1], 'default');
assert.equal(accepted.pageWindow.dataLayer[1][1], 'update');

const returning = scenario('granted');
assert.equal(returning.scripts.length,1,'A prior opt-in should remain respected');
returning.events['analyticsReject:click']();
assert.equal(returning.storage.get('ks-analytics-consent-v1'),'denied');
assert.equal(returning.reloads,1,'Revocation should reload a page with previously active Analytics');
assert.equal(scenario('denied').scripts.length,0,'Revoked visitor should not load Analytics on revisit');

console.log('PASS: no analytics before opt-in, rejection, accept, persistence, preference reopening and revocation.');
