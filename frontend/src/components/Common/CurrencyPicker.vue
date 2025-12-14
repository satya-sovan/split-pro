<template>
  <div class="space-y-2">
    <label v-if="label" class="block text-sm font-medium">
      {{ label }}
    </label>
    <Select :model-value="modelValue" @update:model-value="$emit('update:modelValue', $event)">
      <option v-for="curr in currencies" :key="curr" :value="curr">
        {{ curr }} - {{ getCurrencyName(curr) }}
      </option>
    </Select>
  </div>
</template>

<script setup lang="ts">
import Select from '@/components/ui/Select.vue'
import { CURRENCIES } from '@/lib/currency'

interface Props {
  modelValue: string
  label?: string
  currencies?: readonly string[]
}

const props = withDefaults(defineProps<Props>(), {
  currencies: () => CURRENCIES
})

defineEmits<{
  'update:modelValue': [value: string]
}>()

function getCurrencyName(code: string): string {
  const names: Record<string, string> = {
    USD: 'US Dollar',
    EUR: 'Euro',
    GBP: 'British Pound',
    JPY: 'Japanese Yen',
    AUD: 'Australian Dollar',
    CAD: 'Canadian Dollar',
    CHF: 'Swiss Franc',
    CNY: 'Chinese Yuan',
    SEK: 'Swedish Krona',
    NZD: 'New Zealand Dollar',
    MXN: 'Mexican Peso',
    SGD: 'Singapore Dollar',
    HKD: 'Hong Kong Dollar',
    NOK: 'Norwegian Krone',
    KRW: 'South Korean Won',
    TRY: 'Turkish Lira',
    RUB: 'Russian Ruble',
    INR: 'Indian Rupee',
    BRL: 'Brazilian Real',
    ZAR: 'South African Rand'
  }
  return names[code] || code
}
</script>

