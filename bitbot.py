#!/usr/bin/python3

# BitBot
# by Bitnapper
#
# based on making_a_bot.py by
#
# changing 'Dt. Erstvero ff.' in edition name to 'Deutsche Erstveröffentlichung'

search_pattern="Dt. Erstvero ff."
new_pattern="Deutsche Erstveröffentlichung"

import copy
import gzip

from olclient.bots import AbstractBotJob

class correctEditionName(AbstractBotJob):
	# check if correction is necessary
	@staticmethod
	def needs_correction(edition_name: str) -> bool:
		return( edition_name.find(search_pattern) >= 0 )

	def run(self) -> None:
		self.dry_run_declaration()

		comment = "changing 'Dt. Erstvero ff.' in edition_name to 'Deutsche Erstveröffentlichung'"
		with gzip.open(self.args.file, 'rb') as fin:
			for row in fin:
				row, json_data = self.process_row(row)
				if json_data['type']['key'] != '/type/edition': continue
				if not self.needs_correction(json_data['edition_name']): continue

				# database may have changed, check again
				olid = json_data['key'].split('/')[-1]
				edition = self.ol.Edition.get(olid)
				if edition.type['key'] != '/type/edition': continue # skip deleted
				if not self.needs_correction(edition.edition_name): continue

				# this edition needs editing, so fix it
				old_edition_name = copy.deepcopy(edition.edition_name)
				edition.edition_name.replace(search_pattern, new_pattern)
				self.logger.info('\t'.join([olid, old_edition_name, edition.edition_name])) # don't forget to log modifications!
				self.save(lambda: edition.save(comment=comment))

if '__name__' == __name__:
	job = correctEditionName()

	try:
		job.run()
	except Exception as e:
		job.logger.exception("")
		raise e
