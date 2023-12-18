# Task 1 - article generation

## Introduction:
T1 for short, DarijaBot Task 1 handles the creation of new automated articles, following a text template that can either be in XML, JSON or a text-template embedded on a Wikipedia project page.

This is not the only task that creates automated articles, since T23 for example handles the creation of time-related articles, but it specializes in automated articles that have a free or general format, which has to be defined using a text template, as opposed to T23 where the format is technically predefined and constant using templates.

The ary documentation for this task can be found at: https://w.wiki/8Ydn

## Subclasses and subtasks:
### Subclasses:
There are three types of tasks in the T1 class:
1. T1.1, fixed domain specific tasks: these are tasks that are destined to be run over a fixed batch of topics, and use a static parameterized text. This parameterized text is embedded on a Wikipedia project page that is preceded with the prefix "Wikipedia:text-template-" (or equivalent in the local language). The scripts of these tasks can be discarded as soon as all topics in the target domain are over (e.g. Moroccan villages task)
2. T1.2, flexible domain specific tasks: these are tasks that are more generic, in the sense that sections of the text can be added or replaced depending on the parameter values. Furthermore, in their most complete form, these tasks do not depend on the specific domain exactly, and can be run with a variety of topics, within certain limits (e.g. they may only write biographies, such as the Moroccan politicians task, which could also be extended to other nationalities and types of occupations in principle). The scripts of these tasks are generally long lived and hard to discard, or may need only a bit of tweaking to be used for adjacent topics.
3. T1.3, free writing task(s): potentially the usage of LLMs, such as OpenAI's GPT, could allow the writing of articles of high or acceptable quality using public databases and other data sources. The data may still need to be prepared and cleaned up, and the batches would have to be small enough to be manageable for human review. This is a future task that has not been developed or explored yet.

The choice between different techniques and data formats is still being experimented with.

### Subtasks:
So far the following T1 tasks have been run on arywiki:
* Monuments in Morocco (5 on the main namespace)
* Moroccan politicians (around 15 articles written to draft namespace)
* Cryprocurrencies (30 articles on the main namespace)
* Moroccan villages (1219 articles created on the main namespace)

## Future development
It is envisaged that T1 would leverage the power of LLMs to generate articles for a variety of subjects with Wikidata, or by searching the web. These articles would have to be written to the draft namespace, or generated in small manageable batches to the main namespace with a strict reviewing protocol.
